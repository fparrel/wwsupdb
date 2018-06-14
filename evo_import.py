#!/usr/bin/env python

import json
import pymongo

collection = pymongo.MongoClient().wwsupdb.evo

def insert(id,river):
    collection.update({'_id':id},river,upsert=True)

with open('eauxvives_org.json','r') as f:
    input = json.load(f)

rivers_grouped={}
for river in input:
    if river['name'] in rivers_grouped:
        rivers_grouped[river['name']].append(river)
    else:
        rivers_grouped[river['name']] = [river]

for name,rivers in rivers_grouped.iteritems():
    if len(rivers)>1:
        print 'Duplicate found for', name, ', merging...'
        assert(len(rivers)==2)
        fields = set([field for field in rivers[0]] + [field for field in rivers[1]])
        new_river = {}
        for field in fields:
            if rivers[0].has_key(field) and rivers[1].has_key(field) and rivers[0][field]!=rivers[1][field]:
                new_value = rivers[0][field] + rivers[1][field]
            elif rivers[0].has_key(field):
                new_value = rivers[0][field]
            elif rivers[1].has_key(field):
                new_value = rivers[1][field]
            new_river[field] = new_value
    else:
        assert(len(rivers)==1)
        new_river = rivers[0]
    # sort 'parcours' by name
    new_river['parcours'].sort(key=lambda x:x['name'])
    insert(name,new_river)
