#!/usr/bin/env python
# -*- coding: utf8 -*-

import pymongo
from match_sources import clean4fuzzy
from polygons import is_in_country

def none_or_encode(s):
    if s==None:
        return " "
    else:
        if isinstance(s,basestring):
            return s.encode('utf8')
        else:
            return map(lambda si:si.encode('utf8'),s)

def main():
    input = ('evo','rivermap','ckfiumi','osm')
    merged = 'rivers_merged2'
    db=pymongo.MongoClient().wwsupdb
    rivers={}
    names={}
    cptrs={}
    not_merged={}
    for inp in list(input) + [merged]:
        names[inp] = []
        cptrs[inp] = 0
        not_merged[inp] = []

    # get merged rivers
    qry = {"_id":1}
    for inp in input:
        qry["name_%s"%inp]=1
    for river in db[merged].find({},qry):
        cptrs[merged]+=1
        for inp in input:
            n = river.get("name_%s"%inp)
            if n!=None:
                names[inp].extend(n)
        names['osm'].append(river["_id"])
        river['name_osm'] = [river["_id"]]
        rivers[clean4fuzzy(river["_id"])] = river
    # get remaining input rivers
    for inp in input:
        for river in db[inp].find({},{"_id":1,"situation":1,"routes_rivermap.start":1,"routes_rivermap.end":1}):
            cptrs[inp]+=1
            if river["_id"] not in names[inp]:
                if river["_id"] not in rivers:
                    rivers[clean4fuzzy(river["_id"])] = {"name_%s"%inp:river["_id"]}
                    # Apply filters
                    avoid = False
                    # Filter on situation
                    situation = river.get("situation")
                    if situation!=None and len(situation)>0:
                        if situation[0] not in ('France','Italie') or (len(situation)>1 and situation[1]!='DOM-TOM'):
                            avoid = True
                    # Filter on coordinates
                    routes = river.get("routes_rivermap")
                    if routes!=None and len(routes)>0:
                        avoid = True
                        for route in routes:
                            if is_in_country(("france","italy"),(route["start"]["lat"],route["start"]["lon"])):
                                avoid = False
                                break
                            if is_in_country(("france","italy"),(route["end"]["lat"],route["end"]["lon"])):
                                avoid = False
                                break
                    if not avoid:
                        not_merged[inp].append((clean4fuzzy(river["_id"]),river["_id"]))
                    else:
                        print 'Ignoring %s in %s' % (river["_id"].encode('utf8'), repr(situation))
                else:
                    rivers[clean4fuzzy(river["_id"])]["name_%s"%inp]=river["_id"]
    # Display rivers by alphabetical order
    names_all = rivers.keys()
    names_all.sort()
    f = open('sources.html','w')
    f.write('<!DOCTYPE html>\n')
    f.write('<html><head><style>table, th, td {border: 1px solid black;}</style><meta http-equiv="Content-Type" content="text/html; charset=utf8" /></head><body>')
    f.write('<b>Merged: %s</b><table><tr><th>cleaned name %s</th>'%(cptrs[merged],len(names_all)))
    for inp in input:
        f.write('<th>%s %d</th>'%(inp,cptrs[inp]))
    f.write('</tr>')
    for name in names_all:
        sources = rivers[name]
        f.write('<tr><td>%s</td>'%name.encode('utf8'))
        for inp in input:
            f.write('<td>%s</td>'%none_or_encode(sources.get('name_%s'%inp)))
        f.write('</tr>')
    f.write('</table></body></html>')
    f.close()
    for src in not_merged:
        f = open('notmerged_%s.html'%src,'w')
        f.write('<!DOCTYPE html>\n')
        f.write('<html><head><style>table, th, td {border: 1px solid black;}</style><meta http-equiv="Content-Type" content="text/html; charset=utf8" /></head><body><b>Count: %s / %s</b><table><tr><th>cleaned name</th><th>name</th></tr>' % (len(not_merged[src]),cptrs[src]))
        not_merged[src].sort()
        for cleaned_name,name in not_merged[src]:
            f.write('<tr><td>%s</td><td>%s</td></tr>'%(cleaned_name.encode('utf8'),name.encode('utf8')))
        f.write('</table></body></html>')
        f.close()
    f = open('merged.html','w')
    f.write('<!DOCTYPE html>\n')
    f.write('<html><head><style>table, th, td {border: 1px solid black;}</style><meta http-equiv="Content-Type" content="text/html; charset=utf8" /></head><body><b>Count: %s / %s</b><table><tr><th>cleaned name</th><th>name</th></tr>' % (cptrs[merged],len(names_all)))
    for river in db[merged].find({},{"_id":1}):
        name = river["_id"]
        cleaned_name = clean4fuzzy(name)
        f.write('<tr><td>%s</td><td>%s</td></tr>'%(cleaned_name.encode('utf8'),name.encode('utf8')))
    f.write('</table></body></html>')
    f.close()

if __name__=='__main__':
    main()
