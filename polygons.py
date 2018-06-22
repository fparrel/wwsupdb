#!/usr/bin/env python

from xml.etree import ElementTree as ET
import matplotlib.path as mplPath
import numpy as np

poly_cache = {}

def tolatlon(s):
    s2 = s.split(',')
    return float(s2[1]),float(s2[0])

def polygon(kmlfilename):
    with open(kmlfilename,"r") as f:
        root = ET.parse(f)
    ns='{http://earth.google.com/kml/2.0}'
    return map(tolatlon,root.getroot().find(ns+'Document').find(ns+'Placemark').find(ns+'MultiGeometry').find(ns+'Polygon').find(ns+'outerBoundaryIs').find(ns+'LinearRing').find(ns+'coordinates').text.split())

def contains(poly,point):
    return mplPath.Path(np.array(poly)).contains_point(point)


def is_in_country(ctry_list,point):
    for ctry in ctry_list:
        poly = poly_cache.get(ctry)
        if poly==None:
            poly = polygon('%s.kml'%ctry)
            poly_cache[ctry] = poly
        if contains(poly,point):
            return True
    return False

if __name__=='__main__':
    print contains(polygon("france.kml"),(45.0,0.0))
    print contains(polygon("france.kml"),(30.0,0.0))
    print is_in_country(("france","italy"),(45.0,0.0))
