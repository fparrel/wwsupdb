#!/usr/bin/env python
# -*- coding: utf8 -*-

#~ tomerge = {"Ardèche (haute)":"Ardèche",
           #~ "Ardèche (basse)":"Ardèche",
           #~ "Ariège (Haute)":"Ariège",
           #~ "Garonne - Les Roches":"Garonne",
           #~ 'Rhône (entier)':'Rhône',
           #~ #"Ouvèze de l'ardèche":"Ouvèze",
           #~ "Ouvèze des Baronnies":"Ouvèze", # chez Evo: "Ouvèze des Baronnies" et "Ouvèze" sont la meme riviere
           #~ }
tomerge = {}

import json
import pymongo
from pprint import pprint

collection = pymongo.MongoClient().wwsupdb.evo

def insert(id,river):
    collection.update({'_id':id},river,upsert=True)

def main():

    with open('evo.json','r') as f:
        input = json.load(f)

    rivers_grouped={}
    for river in input:
        new_name = tomerge.get(river['name'].encode('utf8'))
        if new_name!=None:
            river['name'] = new_name
        if river['name'] in rivers_grouped:
            rivers_grouped[river['name']].append(river)
        else:
            rivers_grouped[river['name']] = [river]

    collection.drop()

    for name,rivers in rivers_grouped.iteritems():
        if len(rivers)>1:
            try:
                name_unicode = name.decode('utf8',errors='ignore')
            except:
                name_unicode = name.replace(u'\xe8','e').decode('utf8',errors='ignore')
            name_utf8 = name_unicode.encode('utf8')
            print '%d duplicates found for %s' % (len(rivers),name_utf8)
            b = False
            j = 0
            while not b:
                for i in range(0,len(rivers)):
                    # if j is too big, numerate the rivers
                    if j>=len(rivers[i]['situation']):
                        for i in range(0,len(rivers)):
                            rivers[i]['name'] = '%s (%s)' % (name, i)
                            b = True
                if b:
                    break
                s = [river['situation'][j] for river in rivers]
                if len(set(s))==len(s):
                    # we found a j where all situations[j] are different: add it in the name
                    for i in range(0,len(rivers)):
                        rivers[i]['name'] = '%s (%s)' % (name, rivers[i]['situation'][j])
                    break
                j += 1
            print ','.join(map(lambda river:river['name'],rivers))
        for river in rivers:
            insert(river["name"],river)

if __name__=='__main__':
    main()
