#!/usr/bin/env python

# Sort the rivermap routes by descending order on river path

import pymongo
from geo_utils import ids_on_path

db=pymongo.MongoClient().wwsupdb

for river in db.rivers_merged.find({"name_rivermap":{"$exists":True},"paths":{"$size":1}}):
    for route in river['routes_rivermap']:
        a,b = ids_on_path((route['start']['lat'],route['start']['lon']),(route['end']['lat'],route['end']['lon']),river['paths'][0])
        #print a,b
        route['start']['id'] = [0,a]
        route['end']['id'] = [0,b]
    river['routes_rivermap'].sort(key=lambda route:route['start']['id'][1])
    db.rivers_merged.update({"_id":river["_id"]},river,upsert=True)
