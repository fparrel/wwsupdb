#!/usr/bin/env python

import pymongo,sys,json

client = pymongo.MongoClient()
db = client.wwsupdb2

for river in json.load(open(sys.argv[1],"r")):
    db.rivers.insert(river)

