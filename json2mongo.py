#!/usr/bin/env python

import pymongo,sys,json

client = pymongo.MongoClient()
db = client.wwsupdb

for river in json.load(open(sys.argv[1],"r")):
    db[sys.argv[2]].insert(river)

