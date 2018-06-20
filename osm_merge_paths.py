#!/usr/bin/env python

import pymongo
from merge_paths import merge_paths

collection = pymongo.MongoClient().wwsupdb.osm_raw

for river in collection.find():
    print river['_id'].encode('utf8')
    merge_paths(river['paths'])
    collection.update({"_id":river["_id"]},{"$set":river})
