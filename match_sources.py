#!/usr/bin/env python
# -*- coding: utf8 -*-

#
# Script to map rivers from different sources:
#    osm with rivers from eauxvives.org screen scraping
#    osm with rivers from rivermap.ch screen scraping

# Options

print_not_found = True
#print_not_found = False
console_encoding = 'utf8' #latin1 on Windows
BULK_SIZE = 10

# Hard codes

# Tokens to be ignored, don't forget the trailing space
unsignificant_tokens = ("Rivière d'",'Rivière ','Ruisseau ','Le ','La ',"L'")

# Bad fuzzy matches
exclude_list = (('Garon', 'La Garonne'),('Volp','Volpajola'),('Rauma','Le Raumartin'),('Ostri','Ostriconi'),('Orb','U Fium Orbu'),('Dore','Dorette'))

#TODO: check:
#SRC2: Ligne	SRC1: Le Ligneron
#SRC2: Lieux	SRC1: Le Lieux de Naucelle
#SRC2: Esca	SRC1: Vieil Escaut
#SRC2: Ese	SRC1: Rio Esera
#SRC2: Chasse	SRC1: Le Chassezac
#SRC2: Loire 	SRC1: La Loire - Bras de Pirmil


# End of Hard codes


import json
import sys
from fuzzywuzzy import fuzz

def remove_tokens(s,tokens):
    for token in tokens:
        i = 0
        while i>-1:
            #i = unicode(s).find(unicode(token,encoding='utf8'))
            i = s.find(token)
            if i>-1:
                s=s[:i]+s[i+len(token):]
    return s


def open_source(src_input):
    if src_input[0]=='file':
        with open(src_input[1],'r') as f:
            src_json=json.load(f)
        names_src={}
        for river in src_json:
            if river['name'] in names_src:
                names_src[river['name']] += 1
                river['name'] = '%s_%d' % (river['name'],names_src[river['name']])
                print river['name']
            else:
                names_src[river['name']] = 0
        river_names_src_cache = dict([(river['name'],river) for river in src_json])
        assert(len(river_names_src_cache)==len(src_json))
        def river_names_src():
            for name in river_names_src_cache.keys():
                yield name
        def river_src(id):
            return river_names_src_cache[id]
    elif src_input[0]=='mongo':
        river_names_src_cache = [river['_id'] for river in client.wwsupdb[src_input[1]].find({},{'_id':1})]
        def river_names_src():
            for name in river_names_src_cache:
                yield name
        def river_src(id):
            return client.wwsupdb[src_input[1]].find_one({'_id':id})
    else:
        raise Exception('Input type not handled')
    return river_names_src,river_src

def clean4fuzzy(i):
    return unicode(remove_tokens(i.encode('utf8'),unsignificant_tokens),encoding='utf8')

def match(src1_input,src2_input,output):

    # Prepare data input and output

    # Connect to MongoDB if needed
    if 'mongo' in (src2_input[0],src1_input[0],output[0]):
        import pymongo
        global client
        client = pymongo.MongoClient()

    # Open source 2 data
    river_names_src2,river_src2 = open_source(src2_input)

    # Open source 1 data
    river_names_src1,river_src1 = open_source(src1_input)

    # Prepare output
    if output[0]=='file':
        rivers_output = []
        def river_output(river):
            rivers_output.append(river)
    elif output[0]=='mongo':
        global bulk
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

    for name_src2 in river_names_src2():
        matches = []

        # First try to match with partial_ratio (example: 'The Big River" = "Big River")
        for name_src1 in river_names_src1():
            if fuzz.partial_ratio(clean4fuzzy(name_src2),clean4fuzzy(name_src1)) == 100:
                matches.append(name_src1)

        if len(matches)>0:

            # If there are several matches use ratio instead of partial_ratio and get the best
            if len(matches)>1:
                ratio_matches = map(lambda match: (fuzz.ratio(clean4fuzzy(name_src2),clean4fuzzy(match)),match),matches)
                ratio_matches.sort(reverse=True)
                match = ratio_matches[0][1]
            else:
                match = matches[0]

            name_src1 = match
            if (name_src2,name_src1) in exclude_list:
                print 'Ignoring bad match SRC2: %s\tSRC1: %s' % (name_src2,name_src1)
                continue

            print 'SRC2: %s\tSRC1: %s' % (name_src2.encode(console_encoding), name_src1.encode(console_encoding))

            new_river = river_src1(name_src1)
            assert(new_river!=None)
            id = new_river['_id']
            new_river.update(river_src2(name_src2))
            new_river['name_%s'%src2_input[1]] = new_river['_id'] # add src2 name
            new_river['_id'] = id # keep old _id
            river_output(new_river)

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

def main():
    if len(sys.argv)==7:
        match((sys.argv[1],sys.argv[2]),(sys.argv[3],sys.argv[4]),(sys.argv[5],sys.argv[6]))
    elif len(sys.argv)==2 and sys.argv[1] in ('-h','--help'):
        print 'Usage: %s src1type src1 src2type src2 outtype output' % sys.argv[0]
        print 'Example: %s mongo rivers mongo evo mongo rivers_merged' % sys.argv[0]
    else:
        match(('mongo','rivers'),('mongo','evo','evo'),('mongo','rivers_merged'))
        match(('mongo','rivers'),('mongo','rivermap','rivermap'),('mongo','rivers_merged'))

if __name__=='__main__':
    main()
