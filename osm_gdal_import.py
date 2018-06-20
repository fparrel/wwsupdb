#!/usr/bin/env python

import gdal, ogr
import pymongo
import os

collection = pymongo.MongoClient().wwsupdb.osm_raw

def get_rivers(fname):

    gdal.SetConfigOption('OGR_INTERLEAVED_READING', 'YES')
    osm = ogr.Open(fname)

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
                                yield (name,feat.geometry().GetPoints())

                #The destroy method is necessary for interleaved reading
                feat.Destroy()

                feat = lyr.GetNextFeature()


collection.drop()
for fname in os.listdir('data_osm_pbf') + os.listdir('data_osm_pbf_italy'):
    if fname.endswith('.osm.pbf'):
        print fname
        for name,path in get_rivers('data_osm_pbf/%s'%fname):
            collection.update({"_id":name},{"$push":{"paths":path}},upsert=True)
