#!/usr/bin/env python
# -*- coding: utf8 -*-

from text_utils import clean4fuzzy
from manual_matches import manual_matches
import pymongo
from pprint import pprint

db = pymongo.MongoClient().wwsupdb
bulk = []

def merge(src1,id_src1,src2,id_src2_input,output):
  global bulk
  doc1 = db[src1].find_one({"_id":id_src1})
  if doc1==None:
    try:
      print '%s not found in %s'%(id_src1.encode('utf8'),src1)
    except:
      print '%s not found in %s'%(repr(id_src1),src1)
    return
  if not isinstance(id_src2_input,list):
    id_src2_input = [id_src2_input]
  for id_src2 in id_src2_input:
    doc2 = db[src2].find_one({"_id":id_src2})
    if doc2==None:
      try:
        print '%s not found in %s'%(id_src2.encode('utf8'),src2)
      except:
        print '%s not found in %s'%(repr(id_src2),src2)
      return
    new_doc = {src1:doc1,src2:doc2}
    #new_doc.update(doc1)
    #new_doc.update(doc2)
    #new_doc["name_%s"%src1]=id_src1
    bulk.append(pymongo.UpdateOne({'_id':id_src2},{"$push":{src1:doc1,"name_%s"%src1:id_src1}},upsert=True))
    bulk.append(pymongo.UpdateOne({'_id':id_src2},{"$set":{src2:doc2}},upsert=True))
    if len(bulk)>100:
      try:
        result = db[output].bulk_write(bulk)
      except pymongo.errors.BulkWriteError,e:
        pprint(e.details)
        raise Exception(e)
      bulk = []

def flush():
  global bulk
  if len(bulk)>0:
    db['rivers_merged2'].bulk_write(bulk)
    bulk = []

def main():
  output = 'rivers_merged2'
  input = ('evo','rivermap','ckfiumi')
  input_mandatory = 'osm'

  src_names = {}
  #allnames = set([])
  for src in list(input) + [input_mandatory]:
    src_names[src] = map(lambda n:(clean4fuzzy(n['_id']),n['_id']),list(db[src].find({},{"_id":1})))
    src_names[src].sort(key=lambda x:x[0])
    print src,len(src_names[src])
    #allnames.update(src_names[src])

  db[output].drop()

  i = {}
  for inp in input:
    i[inp] = 0
  for name,fullname in src_names[input_mandatory]:
    #print name.encode('utf8')
    for src in input:
      while i[src]<len(src_names[src]) and name>src_names[src][i[src]][0]:
        i[src] += 1
      if i[src]<len(src_names[src]) and name==src_names[src][i[src]][0]:
        merge(src,src_names[src][i[src]][1],input_mandatory,fullname,output)

  for src in manual_matches:
    for id1,id2 in manual_matches[src].iteritems():
      #print src,id1,'rivers',id2
      merge(src,id1,input_mandatory,id2,output)
  flush()

if __name__=='__main__':
  main()
