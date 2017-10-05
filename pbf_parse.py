from imposm.parser import OSMParser
from geo_utils import link_paths
import json

# simple class that handles the parsed OSM data.
class RiversParser(object):
    rivers = 0

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'waterway' in tags and 'name' in tags:
                if tags['waterway']=='river':
                    rivers[tags['name']].append(refs)

# instantiate counter and parser and start parsing
rivers_parser = RiversParser()
p = OSMParser(concurrency=4, ways_callback=rivers_parser.ways)
p.parse('france-latest.osm.pbf')

# done
print rivers_parser.rivers
rivers_output = []
for river_name,river_paths in rivers_parser.rivers:
    rivers_output.append({'_id':river_name,'paths':link_paths(paths)})

json.dump(rivers_output,open('osm_rivers_fr-from_pbf.json','w'))

# wget http://download.geofabrik.de/europe/france-latest.osm.pbf
