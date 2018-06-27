#!/usr/bin/env python

import json
import pymongo

collection = pymongo.MongoClient().wwsupdb.dc

def insert(id,canyon):
    collection.update({"_id":id},{"$set":canyon},upsert=True)

def main():
    with open('dc.json','r') as f:
        canyons = json.load(f)
    byname = {}
    for canyon in canyons:
        title = canyon['title']
        if byname.has_key(title):
            byname[title].append(canyon)
        else:
            byname[title] = [canyon]
    for title,canyon_list in byname.iteritems():
        if len(canyon_list)>1:
            lprovince = filter(lambda x:x!=None,map(lambda canyon:canyon.get('province_name'),canyon_list))
            lcommune = filter(lambda x:x!=None,map(lambda canyon:canyon.get('commune'),canyon_list))
            if len(set(lprovince))==len(canyon_list):
                for canyon in canyon_list:
                    id = '%s (%s)' % (canyon['title'],canyon['province_name'])
                    insert(id,canyon)
            elif len(set(lcommune))==len(canyon_list):
                for canyon in canyon_list:
                    id = '%s (%s)' % (canyon['title'],canyon['commune'])
                    insert(id,canyon)
        elif len(canyon_list)==1:
            id = canyon_list[0]['title']
            insert(id,canyon_list[0])
        else:
            raise Exception('not handled')

if __name__=='__main__':
    main()
