#!/usr/bin/env python

class Bounds:
    def __init__(self):
        self.latmin = None
        self.latmax = None
        self.lonmin = None
        self.lonmax = None
    def extend(self,path):
        for pt in path:
            if self.latmin == None:
                self.latmin = pt[0]
                self.latmax = pt[0]
                self.lonmin = pt[1]
                self.lonmax = pt[1]
            else:
                if pt[0]<self.latmin:
                    self.latmin = pt[0]
                if pt[0]>self.latmax:
                    self.latmax = pt[0]
                if pt[1]<self.lonmin:
                    self.lonmin = pt[1]
                if pt[1]>self.lonmax:
                    self.lonmax = pt[1]

import pymongo
collection = pymongo.MongoClient().wwsupdb.rivers_merged2
for river in collection.find():
    if river.has_key('osm') and river['osm'].has_key('paths') and len(river['osm']['paths'])>0:
        bounds = Bounds()
        for path in river['osm']['paths']:
            bounds.extend(path)
        b = [bounds.latmin,bounds.latmax,bounds.lonmin,bounds.lonmax]
        collection.update({'_id':river['_id']},{"$set":{'osm.bounds':b}})
