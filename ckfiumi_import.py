#!/usr/bin/env python
# -*- coding: utf8 -*-

# Hard codes

tomerge = {"Pescia di calamecca ":"Pescia",
           "Pescia di pescia":"Pescia",
           "Adda sup.":"Adda",
           "Adda inferiore":"Adda",
           }

# end of hard codes

import json
rivers = {}
for route in json.load(open('ckfiumi.json','r')):
    river_name = route['river_name']
    if river_name in tomerge:
        river_name = tomerge[river_name]
    if river_name in rivers:
        rivers[river_name].append(route)
    else:
        rivers[river_name] = [route]
import pymongo
col = pymongo.MongoClient().wwsupdb.ckfiumi
for river_name,routes in rivers.iteritems():
    routes.sort(key=lambda route:route['order'])
    regions = list(set(map(lambda r:r['region'],routes)))
    provinces = list(set(filter(lambda p:p!=None,map(lambda r:r.get('province'),routes))))
    river = {"_id":river_name,"regions":regions,"provinces":provinces,"routes_ckfiumi":routes}
    col.insert(river)
