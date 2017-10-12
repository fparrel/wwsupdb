# -*- coding: utf8 -*-

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

console_encoding = 'utf8' #latin1 on Windows

# Load data from different sources

rivers_evo=json.load(open('eauxvives_org.json','r'))
rivers_osm=json.load(open('osm_rivers_fr-from_pbf.json','r'))

rivers_output = []

# Try to match

unsignificant_tokens = ['Rivière','Ruisseau']

for river_evo in rivers_evo:
    name_evo = river_evo['name']
    matches = []

    # First try to match with partial_ratio (example: 'The Big River" = "Big River")
    for river_osm in rivers_osm:
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
        print 'evo: %s\tosm: %s' % (name_evo.encode(console_encoding), match[1]['_id'].encode(console_encoding))
        river_evo['name_osm'] = match[1]['_id']
        river_evo.update(match[1])
        rivers_output.append(river_evo)

json.dump(rivers_output,open('rivers-merged.json','w'))
