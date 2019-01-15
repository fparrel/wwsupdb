#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Web interface for updating rivers
#


from config import keysnpwds,config
import sys
import json
import datetime
import copy
from flask import Flask,render_template,send_file,Response,flash,request,redirect,session,abort
from flask_babel import Babel,gettext

if config["data_source"]=="file":
    from serialize_filedump import load_rivers,save_rivers
    ## Rivers cache

    rivers_cache = load_rivers()

    def rivers(name):
        return rivers_cache[name]
elif config["data_source"]=="mongo":
    import pymongo
    client = pymongo.MongoClient()

    def rivers(name):
        try:
            river = client.wwsupdb.rivers_merged2.find_one({"_id":name})
        except pymongo.errors.ServerSelectionTimeoutError:
            abort(504,"MongoDB server not responding")
        if river==None:
            river_osm = client.wwsupdb.osm.find_one({"_id":name})
            river = {"osm":river_osm}
        return river

    def save_river(river):
        client.wwsupdb.rivers_merged2.update({"_id":river['_id']},{"$set":river},upsert=True)

    def save_transform(t):
        client.wwsupdb.transforms.insert({"when":datetime.datetime.now(),"t":t})

# Create flask application
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = 'uploads'
application.secret_key = keysnpwds['secret_key']


## Internationalization (i18n)

babel = Babel(application)



## Map

@application.route('/',defaults={'map_type':'GMaps'})
@application.route('/<map_type>')
def index(map_type):
    return render_template('map.html',map_type=map_type,GMapsApiKey=keysnpwds['GMapsApiKey'],GeoPortalApiKey=keysnpwds['GeoPortalApiKey'])

@application.route('/river/<name>')
def river(name):
    river = rivers(name)
    if river==None:
        abort(404,"River %s not found"%repr(name))
    else:
        return Response(json.dumps(river), mimetype='application/json')

@application.route('/remove_paths/<river_id>/<pathidlist>')
def remove_paths(river_id,pathidlist):
    # Get data and check inputs
    try:
        pathids = map(int,pathidlist.split(','))
    except:
        abort(400,'Cannot parse pathid list')
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    # Save transform: first and last points of paths to remove
    t = {'op':'remove_paths','river_id':river_id,'paths':map(lambda pathid:{'firstpt':river['osm']['paths'][pathid][0],'lastpt':river['osm']['paths'][pathid][-1]},pathids)}
    # Path ids have to be sorted from greater to lower in order to not shift indexes
    pathids.sort(reverse=True)
    # Perform transform
    for pathid in pathids:
        del river['osm']['paths'][pathid]
    # Save
    save_river(river)
    save_transform(t)
    # Returns transformed data
    return Response(json.dumps(river), mimetype='application/json')

@application.route('/merge_paths_a_after_b/<river_id>/<int:path_id_a>/<int:path_id_b>')
def merge_paths_a_after_b(river_id,path_id_a,path_id_b):
    # Get data and check inputs
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    if path_id_a<0 or path_id_a>=len(river['osm']['paths']) or path_id_b<0 or path_id_b>=len(river['osm']['paths']):
        abort(400,'Invalid path ids given')
    # Save transform: first and last points of paths to merge
    t = {'op':'merge_paths_a_after_b','river_id':river_id,'a':{'firstpt':river['osm']['paths'][path_id_a][0],'lastpt':river['osm']['paths'][path_id_a][-1]},'b':{'firstpt':river['osm']['paths'][path_id_b][0],'lastpt':river['osm']['paths'][path_id_b][-1]}}
    # Perfom transform
    river['osm']['paths'][path_id_b].extend(river['osm']['paths'][path_id_a])
    del river['osm']['paths'][path_id_a]
    # Save
    save_river(river)
    save_transform(t)
    # Returns transformed data
    return Response(json.dumps(river), mimetype='application/json')

@application.route('/split_paths/<river_id>/<pathnameslist>')
def split_paths(river_id,pathnameslist):
    # Get data and parse inputs
    try:
        pathnames = pathnameslist.split('^')
    except:
        abort(400,'Cannot parse pathnameslist list')
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    if len(pathnames)!=len(river['osm']['paths']):
        abort(400,"Number of names does't match number of paths")
    splits = []
    # Perform split
    i = 0
    for pathname in pathnames:
        print pathnames,pathname,i
        splits.append({'name':pathname,'firstpt':river['osm']['paths'][i][0],'lastpt':river['osm']['paths'][i][-1]})
        new_river = copy.deepcopy(river)
        new_river['osm']['paths'] = [river['osm']['paths'][i]]
        new_river['_id'] = pathname
        save_river(new_river)
        i += 1
    save_transform({'op':'split_paths','splits':splits})
    return Response('OK')

@application.route('/river/<river_name>/parcours/<int:parcours_id>/<element>/point/<float:lat>/<float:lon>')
def set_river_element_point(river_name,parcours_id,element,lat,lon):
    rivers(river_name)['parcours'][parcours_id][element+'_point']=(lat,lon)
    return Response('OK')

@application.route('/river/<river_name>/parcours/<int:parcours_id>/<element>/point')
def get_river_element_point(river_name,parcours_id,element):
    if rivers(river_name)['parcours'][parcours_id].has_key(element+'_point'):
        return rivers(river_name)['parcours'][parcours_id][element+'_point']
    else:
        abort(404)

@application.route('/boxsearch/<float:minlat>,<float:maxlat>,<float:minlon>,<float:maxlon>')
def box_search(minlat,maxlat,minlon,maxlon):
    out = []
    qry = {"osm.bounds.0":{"$lte":maxlat},"osm.bounds.1":{"$gte":minlat},"osm.bounds.2":{"$lte":maxlon},"osm.bounds.3":{"$gte":minlon}}
    print qry
    for river in client.wwsupdb.rivers_merged2.find(qry):
        out.append(river['_id'])
    return Response(json.dumps(out), mimetype='application/json')

@application.route('/flush')
def flush():
    save_rivers(rivers)


## Program entry point

if __name__ == '__main__':
    # Start web server
    if len(sys.argv)==2:
        if sys.argv[1] in ('-h','--help'):
            print 'Usage: %s [bindingip]' % sys.argv[0]
            exit()
        else:
            host = sys.argv[1]
    else:
        host = "127.0.0.1"
    application.run(port=8080,debug=True,host=host)

