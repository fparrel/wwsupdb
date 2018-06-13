#!/usr/bin/env python
# -*- coding: utf8 -*-

#
# Script to map rivers from different sources:
#    osm with rivers from eauxvives.org screen scraping
#    osm with rivers from rivermap.ch screen scraping

# Options

#src2_input = ('file','eauxvives_org.json','evo')
src2_input = ('mongo','rivermap','rivermap')
src1_input = ('mongo','rivers')
#output = ('file','rivers_merged2.json')
output = ('mongo','rivers_merged')
print_not_found = False
console_encoding = 'utf8' #latin1 on Windows
BULK_SIZE = 10

# Hard codes

# Bad fuzzy matches
exclude_list = (('Garon', 'La Garonne'),('Volp','Volpajola'),('Rauma','Le Raumartin'),('Ostri','Ostriconi'),('Orb','U Fium Orbu'),('Dore','Dorette'))

#TODO: check:
#SRC2: Ligne	SRC1: Le Ligneron
#SRC2: Lieux	SRC1: Le Lieux de Naucelle
#SRC2: Esca	SRC1: Vieil Escaut
#SRC2: Ese	SRC1: Rio Esera
#SRC2: Chasse	SRC1: Le Chassezac


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

src2_dup_list = {'Drac':handleDrac}
#src2_dup_list = {'Inn':TODO}

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
if 'mongo' in (src2_input[0],src1_input[0],output[0]):
    import pymongo
    client = pymongo.MongoClient()

# Open source 2 data
if src2_input[0]=='file':
    with open(src2_input[1],'r') as f:
        src2_json=json.load(f)
    def rivers_src2():
        for river in src2_json:
            yield river
elif src2_input[0]=='mongo':
    def rivers_src2():
        for river in client.wwsupdb[src2_input[1]].find():
            yield river
else:
    raise Exception('Input type not handled')

# Open source 1 data
if src1_input[0]=='file':
    with open(src1_input[1],'r') as f:
        src1_json=json.load(f)
    def rivers_src1():
        for river in src1_json:
            yield river
elif src1_input[0]=='mongo':
    def rivers_src1():
        for river in client.wwsupdb[src1_input[1]].find():
            yield river
else:
    raise Exception('Input type not handled')

# Prepare output
if output[0]=='file':
    rivers_output = []
    def river_output(river):
        rivers_output.append(river)
elif output[0]=='mongo':
    bulk = []
    def river_output(river):
        global bulk
        bulk.append(pymongo.UpdateOne({'_id':river['_id']},{"$set":river},upsert=True))
        if len(bulk) % BULK_SIZE == 0:
            result = client.wwsupdb[output[1]].bulk_write(bulk)
            #if not(result.modified_count+result.upserted_count == BULK_SIZE):
            #    raise Exception("Cannot upsert into mongodb wwsupdb.%s result.modified_count=%s result.upserted_count=%s"%(output[1],result.modified_count,result.upserted_count))
            bulk = []
else:
    raise Exception('Output type not handled')

# Try to match

for river_src2 in rivers_src2():
    name_src2 = river_src2['name']
    matches = []

    # First try to match with partial_ratio (example: 'The Big River" = "Big River")
    for river_src1 in rivers_src1():
        if fuzz.partial_ratio(name_src2,remove_tokens(river_src1['_id'],unsignificant_tokens)) == 100:
            matches.append((river_src1['_id'],river_src1))

    if len(matches)>0:

        # If there are several matches use ratio instead of partial_ratio and get the best
        if len(matches)>1:
            ratio_matches = map(lambda match: (fuzz.ratio(name_src2,remove_tokens(match[0],unsignificant_tokens)),match),matches)
            ratio_matches.sort(reverse=True)
            match = ratio_matches[0][1]
        else:
            match = matches[0]

        if (name_src2,match[1]['_id']) in exclude_list:
            print 'Ignoring bad match SRC2: %s\tSRC1: %s' % (name_src2,match[1]['_id'])
            continue

        print 'SRC2: %s\tSRC1: %s' % (name_src2.encode(console_encoding), match[1]['_id'].encode(console_encoding))

        if name_src2 in src2_dup_list:
            print 'Handling SRC2 duplicate %s' % name_src2
            src2_dup_list[name_src2](river_src2,match[1])
            continue

        match[1]['name_%s'%src2_input[2]] = name_src2
        id = match[1]['_id']
        match[1].update(river_src2)
        match[1]['_id'] = id # keep old _id
        river_output(match[1])

    else:

        if print_not_found:
            print 'SRC2 river %s not found in SRC1' % (name_src2.encode(console_encoding))

if output[0]=='file':
    with open(output[1],'w') as f:
        json.dump(rivers_output,f)
elif output[0]=='mongo':
    bulk_size = len(bulk)
    if bulk_size > 0:
        result = client.wwsupdb[output[1]].bulk_write(bulk)
        #if not(result.modified_count+result.upserted_count == bulk_size):
        #    raise Exception("Cannot upsert into mongodb wwsupdb.%s result.modified_count=%s result.upserted_count=%s"%(output[1],result.modified_count,result.upserted_count))
