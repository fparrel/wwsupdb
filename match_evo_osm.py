#!/usr/bin/env python
# -*- coding: utf8 -*-

#
# Script to map rivers from osm with rivers from eauxvives.org screen scraping
#

# Options

evo_input = ('file','eauxvives_org.json')
osm_input = ('mongo','rivers')
#output = ('file','rivers_merged2.json')
output = ('mongo','rivers_merged')
print_not_found = False
console_encoding = 'utf8' #latin1 on Windows
BULK_SIZE = 10

# Hard codes

# Bad fuzzy matches
exclude_list = (('Garon', 'La Garonne'),('Volp','Volpajola'),('Rauma','Le Raumartin'),('Ostri','Ostriconi'),('Orb','U Fium Orbu'))

# Duplicates and how to handle it
drac_first = None
def handleDrac(evo,osm):
    global drac_first
    if drac_first==None:
        drac_first=evo
    else:
        # Rename P2 and P3 of first "Drac" to P3 and P4 because second Drac has already a P2
        assert(drac_first["parcours"][0]["name"]=="P2")
        drac_first["parcours"][0]["name"] = "P3"
        assert(drac_first["parcours"][1]["name"]=="P3")
        drac_first["parcours"][1]["name"] = "P4"
        osm.update(drac_first)
        osm.update(evo)
        osm['name_evo'] = evo["name"]
        river_output(osm)

evo_dup_list = {'Drac':handleDrac}

unsignificant_tokens = ['Rivière','Ruisseau']

# End of Hard codes


import json
from fuzzywuzzy import fuzz

def remove_tokens(s,tokens):
    for token in tokens:
        i = 0
        while i>-1:
            i = unicode(s).find(unicode(token,encoding='utf8'))
            if i>-1:
                s=s[:i]+s[i+len(token):]
    return s

# Prepare data input and output

# Connect to MongoDB if needed
if 'mongo' in (evo_input[0],osm_input[0],output[0]):
    import pymongo
    client = pymongo.MongoClient()

# Open evo data
if evo_input[0]=='file':
    with open(evo_input[1],'r') as f:
        rivers_evo_json=json.load(f)
    def rivers_evo():
        for river in rivers_evo_json:
            yield river
elif evo_input[0]=='mongo':
    def rivers_evo():
        for river in client.wwsupdb[evo_input[1]].find():
            yield river
else:
    raise Exception('Input type not handled')

# Open osm data
if osm_input[0]=='file':
    with open(osm_input[1],'r') as f:
        rivers_osm_json=json.load(f)
    def rivers_osm():
        for river in rivers_osm_json:
            yield river
elif osm_input[0]=='mongo':
    def rivers_osm():
        for river in client.wwsupdb[osm_input[1]].find():
            yield river
else:
    raise Exception('Input type not handled')

if output[0]=='file':
    rivers_output = []
    def river_output(river):
        rivers_output.append(river)
elif output[0]=='mongo':
    bulk = []
    def river_output(river):
        global bulk
        bulk.append(pymongo.ReplaceOne({'_id':river['_id']},river,upsert=True))
        if len(bulk) % BULK_SIZE == 0:
            result = client.wwsupdb[output[1]].bulk_write(bulk)
            if not(result.modified_count+result.upserted_count == BULK_SIZE):
                raise Exception("Cannot upsert into mongodb wwsupdb.%s result.modified_count=%s result.upserted_count=%s"%(output[1],result.modified_count,result.upserted_count))
            bulk = []
else:
    raise Exception('Output type not handled')

# Try to match

for river_evo in rivers_evo():
    name_evo = river_evo['name']
    matches = []

    # First try to match with partial_ratio (example: 'The Big River" = "Big River")
    for river_osm in rivers_osm():
        if fuzz.partial_ratio(name_evo,remove_tokens(river_osm['_id'],unsignificant_tokens)) == 100:
            matches.append((river_osm['_id'],river_osm))

    if len(matches)>0:

        # If there are several matches use ratio instead of partial_ratio and get the best
        if len(matches)>1:
            ratio_matches = map(lambda match: (fuzz.ratio(name_evo,remove_tokens(match[0],unsignificant_tokens)),match),matches)
            ratio_matches.sort(reverse=True)
            match = ratio_matches[0][1]
        else:
            match = matches[0]

        if (name_evo,match[1]['_id']) in exclude_list:
            print 'Ignoring bad match evo: %s\tosm: %s' % (name_evo,match[1]['_id'])
            continue

        print 'evo: %s\tosm: %s' % (name_evo.encode(console_encoding), match[1]['_id'].encode(console_encoding))

        if name_evo in evo_dup_list:
            print 'Handling EVO duplicate %s' % name_evo
            evo_dup_list[name_evo](river_evo,match[1])
            continue

        match[1]['name_evo'] = name_evo
        match[1].update(river_evo)
        river_output(match[1])

    else:

        if print_not_found:
            print 'EVO river %s not found in OSM' % (name_evo.encode(console_encoding))

if output[0]=='file':
    with open(output[1],'w') as f:
        json.dump(rivers_output,f)
elif output[0]=='mongo':
    bulk_size = len(bulk)
    if bulk_size > 0:
        result = client.wwsupdb[output[1]].bulk_write(bulk)
        if not(result.modified_count+result.upserted_count == bulk_size):
            raise Exception("Cannot upsert into mongodb wwsupdb.%s result.modified_count=%s result.upserted_count=%s"%(output[1],result.modified_count,result.upserted_count))
