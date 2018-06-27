#!/usr/bin/env python

import pymongo
input = 'rivers_merged2'
cptr = 0
cptr_all = 0
for river in pymongo.MongoClient().wwsupdb[input].find():
    allpoints = []
    if river.has_key('paths'):
        paths = ['paths']
    elif river.has_key('osm'):
        paths = river['osm']['paths']
    else:
        print 'Ignoring %s'%repr(river['_id'])
        continue
    cptr_all += 1
    if len(paths)>1:
        paths = [map(tuple,path) for path in paths]
        for path in paths:
            allpoints.extend(path)
        l = len(allpoints)
        ls = len(set(allpoints))
        if l-ls>0:
            cptr += 1
            print repr(river['_id']),l-ls,l,ls
print '%d/%d'%(cptr,cptr_all)
