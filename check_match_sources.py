#!/usr/bin/env python
import pymongo
from match_sources import clean4fuzzy

def none_or_encode(s):
    if s==None:
        return " "
    else:
        return s.encode('utf8')

def main():
    db=pymongo.MongoClient().wwsupdb
    rivers={}
    names_osm=[]
    names_evo=[]
    names_rivermap=[]
    cptrs = {'osm':0,'evo':0,'rivermap':0,'ckfiumi':0,'merged':0}
    # get merged rivers
    for river in db.rivers_merged.find({},{"_id":1,"name_evo":1,"name_rivermap":1}):
        cptrs['merged']+=1
        river["name_osm"]=river["_id"]
        names_osm.append(river["_id"])
        if river.has_key("name_evo"):
            names_evo.append(river["name_evo"])
        if river.has_key("name_rivermap"):
            names_rivermap.append(river["name_rivermap"])
        rivers[clean4fuzzy(river["_id"])] = river
    # get remaining evo rivers
    for river in db.evo.find({},{"_id":1}):
        cptrs['evo']+=1
        if river["_id"] not in names_evo:
            if river["_id"] not in rivers:
                rivers[clean4fuzzy(river["_id"])] = {"name_evo":river["_id"]}
            else:
                rivers[clean4fuzzy(river["_id"])]["name_evo"]=river["_id"]
    # get remaining rivermap rivers
    for river in db.rivermap.find({},{"_id":1}):
        cptrs['rivermap']+=1
        if river["_id"] not in names_rivermap:
            if river["_id"] not in rivers:
                rivers[clean4fuzzy(river["_id"])] = {"name_rivermap":river["_id"]}
            else:
                rivers[clean4fuzzy(river["_id"])]["name_rivermap"]=river["_id"]
    # get remaining rivermap rivers
    for river in db.rivermap.find({},{"_id":1}):
        cptrs['ckfiumi']+=1
        if river["_id"] not in names_rivermap:
            if river["_id"] not in rivers:
                rivers[clean4fuzzy(river["_id"])] = {"name_ckfiumi":river["_id"]}
            else:
                rivers[clean4fuzzy(river["_id"])]["name_ckfiumi"]=river["_id"]
    # get remaining osm rivers
    for river in db.rivers.find({},{"_id":1}):
        cptrs['osm']+=1
        if river["_id"] not in names_osm:
            if river["_id"] not in rivers:
                rivers[clean4fuzzy(river["_id"])] = {"name_osm":river["_id"]}
            else:
                rivers[clean4fuzzy(river["_id"])]["name_osm"]=river["_id"]
    # Display rivers by alphabetical order
    names = rivers.keys()
    names.sort()
    print '<!DOCTYPE html>'
    print '<html><head><style>table, th, td {border: 1px solid black;}</style><meta http-equiv="Content-Type" content="text/html; charset=utf8" /></head><body><b>Merged: %s</b><table><tr><th>cleaned name %s</th><th>evo %s</th><th>rivermap %s</th><th>ckfiumi %s</th><th>osm %s</th></tr>' % (cptrs['merged'],len(names),cptrs['evo'],cptrs['rivermap'],cptrs['ckfiumi'],cptrs['osm'])
    for name in names:
        sources = rivers[name]
        print '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'% (name.encode('utf8'),none_or_encode(sources.get('name_evo')),none_or_encode(sources.get('name_rivermap')),none_or_encode(sources.get('name_ckfiumi')),none_or_encode(sources.get('name_osm')))
    print '</table></body></html>'

if __name__=='__main__':
    main()
