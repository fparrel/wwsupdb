#!/usr/bin/env python

import pymongo
from merge_paths import merge_paths
from remove_loops import remove_loops

collection = pymongo.MongoClient().wwsupdb.osm

for river in collection.find():
    print river['_id'].encode('utf8')
    merge_paths(river['paths'])
    remove_loops(river)
    collection.update({"_id":river["_id"]},{"$set":river})

