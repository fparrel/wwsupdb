#!/usr/bin/env python

import json,sys
from geo_utils import GeodeticDistGreatCircle

def merge_paths(paths):
    old_len = len(paths)+1
    while len(paths)<old_len:
        old_len = len(paths)
        b = False
        for i in range(0,len(paths)):
            for j in range(0,len(paths)):
                if paths[i][-1] == paths[j][0]:
                    # merge j into i
                    paths[i].extend(paths[j])
                    del paths[j]
                    b = True
                    break
                if paths[i][0] == paths[j][-1]:
                    # merge i into j
                    paths[j].extend(paths[i])
                    del paths[i]
                    b = True
                    break
                #~ # find overlaping paths
                #~ begin_i = -1
                #~ k = 0
                #~ while k < len(paths[i]):
                    #~ l = 0
                    #~ while l < len(paths[j]):
                        #~ #print k,l
                        #~ if paths[i][k]==paths[j][l]:
                            #~ begin_i = k
                            #~ begin_j = l
                            #~ #print 'common got',k,l
                            #~ break
                        #~ l += 1
                    #~ if begin_i!=-1:
                        #~ begin_i = 280 # special case for durance
                        #~ m = 0
                        #~ while begin_i+m < len(paths[i]) and begin_j+m < len(paths[j]) and paths[i][begin_i+m]==paths[j][begin_j+m]:
                            #~ m+=1
                        #~ if m>1:
                            #~ print 'removing',begin_i,begin_j,m
                            #~ del paths[i][begin_i:m]
                            #~ #del paths[j][begin_j:m]
                        #~ break
                    #~ k += 1
            if b:
                break

if __name__=='__main__':
    paths = [
        [[43.4811089,6.2341841],[43.4791642,6.269513300000001]],
        [[43.4810078,6.2909265],[43.433249700000005,6.3642313]],
        [[43.433249700000005,6.3642313],[43.4301522,6.374260100000001]],
        [[43.4791642,6.269513300000001],[43.4810078,6.2909265]],
        [[43.4219713,6.385425000000001],[43.4473507,6.4570821]],
        [[43.484489700000005,6.2144158],[43.4811089,6.2341841]],
        [[43.482820100000005,6.2124755],[43.484489700000005,6.2144158]],
        [[43.448267,6.458647],[43.4473235,6.4624787]],
        [[43.4473507,6.4570821],[43.448267,6.458647]],
        [[43.4301522,6.374260100000001],[43.4219713,6.385425000000001]],
        [[43.4664475,6.568304800000001],[43.4694493,6.571972400000001]],
        [[43.4694493,6.571972400000001],[43.4097165,6.737053400000001]],
        [[43.4484951,6.5457362],[43.4664475,6.568304800000001]],
        [[43.465827100000006,6.116036500000001],[43.482820100000005,6.2124755]],
        [[43.5192727,5.9953338],[43.465827100000006,6.116036500000001]],
        [[43.4473235,6.4624787],[43.431793000000006,6.5228108]],
        [[43.431793000000006,6.5228108],[43.4484951,6.5457362]],
        [[43.5273686,5.984377800000001],[43.5192727,5.9953338]],
        [[43.494067300000005,5.9142226],[43.490663100000006,5.925452]],
        [[43.5028408,5.9086786],[43.494067300000005,5.9142226]],
        [[43.5131151,5.963614300000001],[43.5273686,5.984377800000001]],
        [[43.490663100000006,5.925452],[43.4991374,5.950354300000001]],
        [[43.4991374,5.950354300000001],[43.5131151,5.963614300000001]],
        [[43.504062700000006,5.9073365],[43.5028408,5.9086786]],
    ]
    print 'bf merge',len(paths)
    merge_paths(paths)
    print 'af merge',len(paths)
    import pymongo
    paths = pymongo.MongoClient().wwsupdb.rivers_merged2.find_one({"_id":"La Durance"})["osm"]["paths"]
    paths = [map(tuple,path) for path in paths]
    print 'bf merge',len(paths)
    merge_paths(paths)
    print 'af merge',len(paths)
