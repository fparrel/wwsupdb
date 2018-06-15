#!/usr/bin/env python

import pymongo,sys
from geo_utils import len_of_path,len_btw_2pts

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
