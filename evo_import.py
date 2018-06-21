#!/usr/bin/env python
# -*- coding: utf8 -*-

tomerge = {"Ardèche (haute)":"Ardèche",
           "Ardèche (basse)":"Ardèche",
           "Ariège (Haute)":"Ariège",
           "Garonne - Les Roches":"Garonne",
           'Rhône (entier)':'Rhône',
           #"Ouvèze de l'ardèche":"Ouvèze",
           "Ouvèze des Baronnies":"Ouvèze", # chez Evo: "Ouvèze des Baronnies" et "Ouvèze" sont la meme riviere
           }

import json
import pymongo
from pprint import pprint

collection = pymongo.MongoClient().wwsupdb.evo

def insert(id,river):
    collection.update({'_id':id},river,upsert=True)

with open('evo.json','r') as f:
    input = json.load(f)

rivers_grouped={}
for river in input:
    new_name = tomerge.get(river['name'].encode('utf8'))
    if new_name!=None:
        river['name'] = new_name
        #print '"%s"' % river['name'].encode('latin1')
    if river['name'] in rivers_grouped:
        rivers_grouped[river['name']].append(river)
    else:
        rivers_grouped[river['name']] = [river]

for name,rivers in rivers_grouped.iteritems():
    if len(rivers)>1:
        #pprint(name)
        try:
            name_unicode = name.decode('utf8',errors='ignore')
        except:
            name_unicode = name.replace(u'\xe8','e').decode('utf8',errors='ignore')
        name_utf8 = name_unicode.encode('utf8')
        print '%d duplicates found for %s, merging...' % (len(rivers),name_utf8)
        new_river = {"duplicates":rivers}
        #continue
        #~ fields = set([])
        #~ for river in rivers:
            #~ fields.union([field for field in river])
        #~ assert(len(rivers)==2)
        #~ new_river = {}
        #~ for field in fields:
            #~ for river in rivers:
                
            #~ if rivers[0].has_key(field) and rivers[1].has_key(field) and rivers[0][field]!=rivers[1][field]:
                #~ new_value = rivers[0][field] + rivers[1][field]
            #~ elif rivers[0].has_key(field):
                #~ new_value = rivers[0][field]
            #~ elif rivers[1].has_key(field):
                #~ new_value = rivers[1][field]
            #~ new_river[field] = new_value
    else:
        assert(len(rivers)==1)
        new_river = rivers[0]
    # sort 'parcours' by name
    #new_river['parcours'].sort(key=lambda x:x['name'])
    insert(name,new_river)
