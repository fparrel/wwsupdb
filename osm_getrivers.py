import requests
import re
import json
from geo_utils import link_paths

RIVERREGEX = re.compile('<a target="map" href="queryinmap.php\?BBOX=[0-9\.,\+]+&name=([A-Za-z0-9%%+-]+)&key=waterway&value=river&types=lines">(.*)</a>')
LINESTRINGREGEX = re.compile('<LineString><coordinates>(.*)</coordinates>')


def get_rivers_wmflabs(bbox):
    # Get list of rivers on bbox
    print 'Get rivers list...'
    r = requests.get('http://tools.wmflabs.org/query2map/index.php?key=waterway&value=river&types=lines&BBOX=%f%%2C%f%%2C%f%%2C%f'%bbox)
    t = r.text.encode(r.encoding)
    for river in RIVERREGEX.findall(t):
        print river[1]
        # Get path of river
        r = requests.get('http://tools.wmflabs.org/query2map/osm-to-kml.php?BBOX=%f,%f,%f,%f&name=%s&key=waterway&value=river&types=lines'%(bbox[0],bbox[1],bbox[2],bbox[3],river[0]))
        t = r.text
        lines = LINESTRINGREGEX.findall(t)
        #print len(lines)
        paths = map(lambda linestrsplitted: map(lambda xvy:map(float,xvy.split(',')),linestrsplitted),map(lambda linestr: linestr.split(' '),lines))
        #line = map(lambda xvy:map(float,xvy.split(',')),map(lambda linestr: linestr.split(' '),lines))
        yield {'_id':river[1],'paths':link_paths(paths)}

def get_rivers_pbf():
    pass

def main():
    dept06_fr = (6.559029,43.455733,7.734566,44.363941)
    france = (-7.84,42.27,8.25,51.18)
    #bbox = dept06_fr
    #json.dump(list(get_rivers(bbox)),open('osm_rivers_06-3.json','w'))
    bbox = france
    json.dump(list(get_rivers_wmflabs(bbox)),open('osm_rivers_fr.json','w'))

if __name__=='__main__':
    main()
