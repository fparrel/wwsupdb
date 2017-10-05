import json
from fuzzywuzzy import fuzz

console_encoding = 'latin1'

# Load data from different sources

rivers_evo=json.load(open('eauxvives_org2.json','r'))
rivers_osm=json.load(open('osm_rivers_06-3.json','r'))

rivers_output = []

# Try to match

for river_evo in rivers_evo:
    name_evo = river_evo['name']
    matches = []

    # First try to match with partial_ratio (example: 'The Big River" = "Big River")
    for river_osm in rivers_osm:
        if fuzz.partial_ratio(name_evo,river_osm['_id']) == 100:
            matches.append((river_osm['_id'],river_osm))

    if len(matches)>0:

        # If there are several matches use ratio instead of partial_ratio and get the best
        if len(matches)>1:
            ratio_matches = map(lambda match: (fuzz.ratio(name_evo,match[0]),match),matches)
            ratio_matches.sort(reverse=True)
            match = ratio_matches[0][1]
        else:
            match = matches[0]
        print name_evo.encode(console_encoding), match[1]['_id'].encode(console_encoding)
        river_evo['name_osm'] = match[1]['_id']
        river_evo.update(match[1])
        rivers_output.append(river_evo)

json.dump(rivers_output,open('rivers-merged.json','w'))
