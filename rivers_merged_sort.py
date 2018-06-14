#!/usr/bin/env python

import pymongo
from len_on_river import dist

db=pymongo.MongoClient().wwsupdb

def ids_on_path(a,b,path):
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
  #if not(i_a<i_b):
  #  raise Exception("Input points must be given in the descending order")
  if min_dist_a<1000 and min_dist_b<1000:
      return i_a,i_b
  else:
      return -1,-1

for river in db.rivers_merged.find({"name_rivermap":{"$exists":True},"paths":{"$size":1}}):
    for route in river['routes_rivermap']:
      a,b = ids_on_path((route['start']['lat'],route['start']['lon']),(route['end']['lat'],route['end']['lon']),river['paths'][0])
      #print a,b
      route['start']['id'] = [0,a]
      route['end']['id'] = [0,b]
    river['routes_rivermap'].sort(key=lambda route:route['start']['id'][1])