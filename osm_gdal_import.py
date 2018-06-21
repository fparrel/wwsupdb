#!/usr/bin/env python

import gdal, ogr
import pymongo
import os
import sys

collection = pymongo.MongoClient().wwsupdb.osm_raw

def get_rivers(fname):

    gdal.SetConfigOption('OGR_INTERLEAVED_READING', 'YES')
    osm = ogr.Open(fname)
    if osm==None:
        raise Exception("Cannot open %s"%fname)

    # Grab available layers in file
    nLayerCount = osm.GetLayerCount()

    thereIsDataInLayer = True

    rivers = []

    while thereIsDataInLayer:

        thereIsDataInLayer = False

        # Cycle through available layers
        for iLayer in xrange(nLayerCount):

            lyr = osm.GetLayer(iLayer)

            # Get first feature from layer
            feat = lyr.GetNextFeature()

            while (feat is not None):

                thereIsDataInLayer = True

                #Do something with feature
                if 'waterway' in feat.keys():
                    waterway = feat.GetFieldAsString('waterway')
                    if waterway in ('stream','river'):
                        if 'name' in feat.keys():
                            name = feat.GetFieldAsString('name')
                            if len(name)>0:
                                yield (name,map(lambda pt:(pt[1],pt[0]),feat.geometry().GetPoints()))

                #The destroy method is necessary for interleaved reading
                feat.Destroy()

                feat = lyr.GetNextFeature()

def process(fname):
    bulk = []
    print fname
    for name,path in get_rivers(fname):
        bulk.append(pymongo.UpdateOne({'_id':name},{"$push":{"paths":path}},upsert=True))
        if len(bulk)>100:
            try:
                collection.bulk_write(bulk)
            except pymongo.errors.BulkWriteError,e:
                pprint(e.details)
                raise Exception(e)
            bulk = []
    collection.bulk_write(bulk)

def main():
    if len(sys.argv)==1:
        collection.drop()
        for fname in os.listdir('data_osm_pbf'):
            if fname.endswith('.osm.pbf'):
                process('data_osm_pbf/%s' % fname)
    else:
        process(sys.argv[1])

if __name__=='__main__':
    main()
