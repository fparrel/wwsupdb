#!/usr/bin/env python

import pymongo,sys
from math import sin,cos,atan2,sqrt

def GeodeticDistGreatCircle(lat1,lon1,lat2,lon2):
  "Compute distance between two points of the earth geoid (approximated to a sphere)"
  # convert inputs in degrees to radians
  lat1 = lat1 * 0.0174532925199433
  lon1 = lon1 * 0.0174532925199433
  lat2 = lat2 * 0.0174532925199433
  lon2 = lon2 * 0.0174532925199433
  # just draw a schema of two points on a sphere and two radius and you'll understand
  a = sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
  c = 2 * atan2(sqrt(a), sqrt(1-a))
  # earth mean radius is 6371 km
  return 6372795.0 * c

def dist(pt1,pt2):
  "Compute distance between two points in form of tuples of (lat,lon)"
  return GeodeticDistGreatCircle(pt1[0],pt1[1],pt2[0],pt2[1])

def len_of_path(path):
  "Compute length of a path given in form of array of tuples of (lat,lon)"
  l = 0.0
  for i in range(0,len(path)-1):
    l += dist(path[i],path[i+1])
  return l

def len_btw_2pts(a,b,path):
  "Compute length on a path given in form of array of tuples of (lat,lon), between the 2 closest points"
  min_dist_a = 6000000 # More than 6000km is almost impossible on Earth
  min_dist_b = 6000000
  i=0
  for pt in path:
    d = dist(a,pt)
    if d<min_dist_a:
      min_dist_a = d
      i_a = i
    d = dist(b,pt)
    if d<min_dist_b:
      min_dist_b = d
      i_b = i
    i += 1
  #print i_a,i_b,min_dist_a,min_dist_b
  if not(i_a<i_b):
    raise Exception("Input points must be given in the descending order")
  return len_of_path(path[i_a:i_b])

def main():

  # Parse arguments or display help
  if len(sys.argv)==6:
    name=sys.argv[1]
    a=[float(sys.argv[2].rstrip(",")),float(sys.argv[3])]
    b=[float(sys.argv[4].rstrip(",")),float(sys.argv[5])]
  elif len(sys.argv)==2:
    if sys.argv[1] in ('-h','--help'):
      print 'Usage: %s "River name" lat1 lon1 lat2 lon2' % sys.argv[0]
      return
    else:
      name=sys.argv[1]
      a=None
      b=None
  else:
    name="L'Argens"
    a=[43.521964, 5.982165]
    b=[43.471221, 6.099240]

  # Connect to db
  client = pymongo.MongoClient()
  db = client.wwsupdb

  # Get river from db
  river = db.rivers.find_one({"_id":name})
  if river==None:
    print 'River not found in db'
    return

  # Sanity check
  if not(len(river["paths"])==1):
    print 'Only implemented for 1 single path rivers'
    return

  path=river["paths"][0]

  if a==None:
    # Compute full length of river
    print "%.3f km" % (len_of_path(path)/1000)
  else:
    # Compute partial length on river
    print "%.3f km" % (len_btw_2pts(a,b,path)/1000)

if __name__=='__main__':
  main()
