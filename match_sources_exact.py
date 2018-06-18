#!/usr/bin/env python
# -*- coding: utf8 -*-

from text_utils import clean4fuzzy
from manual_matches import manual_matches
import pymongo

db = pymongo.MongoClient().wwsupdb
bulk = []

def merge(src1,id_src1,src2,id_src2):
  global bulk
  doc1 = db[src1].find_one({"_id":id_src1})
  if doc1==None:
    print '%s not found'%id_src1.encode('utf8')
    return
  doc2 = db[src2].find_one({"_id":id_src2})
  if doc2==None:
    print '%s not found'%id_src2.encode('utf8')
    return
  doc2.update(doc1)
  doc2["_id"]=id_src2
  doc2["name_%s"%src1]=id_src1
  bulk.append(pymongo.UpdateOne({'_id':id_src2},{"$set":doc2},upsert=True))
  if len(bulk)>100:
    db['rivers_merged'].bulk_write(bulk)
    bulk = []

def flush():
  global bulk
  if len(bulk)>0:
    db['rivers_merged'].bulk_write(bulk)
    bulk = []

src_names = {}
#allnames = set([])
for src in ('evo','rivermap','ckfiumi','rivers'):
  src_names[src] = map(lambda n:(clean4fuzzy(n['_id']),n['_id']),list(db[src].find({},{"_id":1})))
  src_names[src].sort(key=lambda x:x[0])
  print src,len(src_names[src])
  #allnames.update(src_names[src])


i = {'evo':0,'rivermap':0,'ckfiumi':0}#,'osm':0}
allnames=src_names['rivers']
for name,fullname in allnames:
  #print name.encode('utf8')
  for src in ('evo','rivermap','ckfiumi'):
    while i[src]<len(src_names[src]) and name>src_names[src][i[src]][0]:
      i[src] += 1
    if i[src]<len(src_names[src]) and name==src_names[src][i[src]][0]:
      merge(src,src_names[src][i[src]][1],'rivers',fullname)

for src in manual_matches:
  for id1,id2 in manual_matches[src].iteritems():
    print src,id1,'rivers',id2
    merge(src,id1,'rivers',id2)
flush()
