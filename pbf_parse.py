#!/usr/bin/env python

#
# Parse a .pbf file from openstreetmaps and output a .json file with rivers
#

input_filename = 'france-latest.osm.pbf'
# ^ got with: wget http://download.geofabrik.de/europe/france-latest.osm.pbf
output_filename = 'osm_rivers_fr-from_pbf.json'


from imposm.parser import OSMParser
from geo_utils import link_paths
import json
import datetime

# simple class that handles the parsed OSM data.
class RiversParser(object):
    def __init__(self):
        self.rivers = {}
        self.coords = {}
    def ways(self, ways):
        #print 'ways'
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'waterway' in tags and 'name' in tags:
                if tags['waterway']=='river':
                    if tags['name'] in self.rivers:
                        self.rivers[tags['name']].append(refs)
                    else:
                        self.rivers[tags['name']] = [refs]
    def coords(self, coords):
        print 'coords'
        for osm_id, lon, lat in coords:
            print osm_id
            self.coords[osm_id] = (lat, lon)
    def nodes(self, nodes):
        print 'nodes'

# instantiate counter and parser and start parsing
rivers_parser = RiversParser()
p = OSMParser(concurrency=4, ways_callback=rivers_parser.ways, coords_callback=rivers_parser.coords, nodes_callback=rivers_parser.nodes)
print 'Parsing... %s' % datetime.datetime.now()
p.parse(input_filename)

print 'Building... %s' % datetime.datetime.now()
rivers_output = []
for river_name,river_paths in rivers_parser.rivers.iteritems():
    paths_ref = link_paths(river_paths)
    paths_coords = []
    for path_ref in paths_ref:
        coords = []
        for ref in path_ref:
            if ref in rivers_parser.coords:
                coords.append(rivers_parser.coords[ref])
            else:
                pass
                #print 'Ref %s not found in coords'%ref
        paths_coords.append(coords)
    rivers_output.append({'_id':river_name,'paths':paths_coords})

print 'Saving...'
with open(output_filename,'w') as f:
    json.dump(rivers_output,f)
