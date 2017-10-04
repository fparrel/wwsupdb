import requests
import re
import json

RIVERREGEX = re.compile('<a target="map" href="queryinmap.php\?BBOX=[0-9\.,\+]+&name=([A-Za-z0-9%%+-]+)&key=waterway&value=river&types=lines">(.*)</a>')
#RIVERREGEX = re.compile('target="(.*)"')
LINESTRINGREGEX = re.compile('<LineString><coordinates>(.*)</coordinates>')

def get_rivers(bbox):
    # Get list of rivers on bbox
    r = requests.get('http://tools.wmflabs.org/query2map/index.php?key=waterway&value=river&types=lines&BBOX=%f%%2C%f%%2C%f%%2C%f'%bbox)
    t = r.text.encode(r.encoding)
    for river in RIVERREGEX.findall(t):
        print river
        # Get path of river
        r = requests.get('http://tools.wmflabs.org/query2map/osm-to-kml.php?BBOX=%f,%f,%f,%f&name=%s&key=waterway&value=river&types=lines'%(bbox[0],bbox[1],bbox[2],bbox[3],river[0]))
        t = r.text
        lines = LINESTRINGREGEX.findall(t)
        print len(lines)
        paths = map(lambda linestrsplitted: map(lambda xvy:map(float,xvy.split(',')),linestrsplitted),map(lambda linestr: linestr.split(' '),lines))
        #line = map(lambda xvy:map(float,xvy.split(',')),map(lambda linestr: linestr.split(' '),lines))
        yield {'_id':river[1],'paths':paths}



def main():
    rivers = json.load(open('osm_rivers_06.json','r'))
    for river in rivers:
        for i in range(0,len(river['paths'])):
            for j in range(0,len(river['paths'])):
                if i!=j and len(river['paths'][i])>0 and len(river['paths'][j])>0 and river['paths'][j][0] == river['paths'][i][-1]:
                    river['paths'][i] += river['paths'][j]
                    river['paths'][j] = []
                elif i!=j and len(river['paths'][i])>0 and len(river['paths'][j])>0 and river['paths'][i][0] == river['paths'][j][-1]:
                    river['paths'][j] += river['paths'][i]
                    river['paths'][i] = []
        paths = filter(lambda path:len(path)>0,river['paths'])
        assert(sum(map(len,river['paths']))==sum(map(len,paths)))
        river['paths']=paths
    json.dump(rivers,open('osm_rivers_06-2.json','w'))
    exit()
    
    dept06_fr = (6.559029,43.455733,7.734566,44.363941)
    france = (-7.84,42.27,8.25,51.18)
    bbox = dept06_fr
    json.dump(list(get_rivers(bbox)),open('osm_rivers_06_tmp.json','w'))
    #bbox = france
    #json.dump(list(get_rivers(bbox)),open('osm_rivers_fr.json','w'))

if __name__=='__main__':
    main()
