#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Web interface for updating rivers
#


try:
    from config import keysnpwds,config
except:
    print 'You must define keysnpwds in config.py'
    exit()
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
        #if river==None:
        #    river = client.wwsupdb.rivers.find_one({"_id":name})
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
        abort(404)
    else:
        return Response(json.dumps(river), mimetype='application/json')

@application.route('/remove_paths/<river_id>/<pathidlist>')
def remove_paths(river_id,pathidlist):
    try:
        pathids = map(int,pathidlist.split(','))
    except:
        abort(400,'Cannot parse pathid list')
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    # Path ids have to be sorted from greater to lower in order to not shift indexes
    pathids.sort(reverse=True)
    for pathid in pathids:
        del river['osm']['paths'][pathid]
    save_river(river)
    save_transform(['remove_paths',river_id,pathids])
    return Response(json.dumps(river), mimetype='application/json')

@application.route('/merge_paths_a_after_b/<river_id>/<int:path_id_a>/<int:path_id_b>')
def merge_paths_a_after_b(river_id,path_id_a,path_id_b):
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    if path_id_a<0 or path_id_a>=len(river['osm']['paths']) or path_id_b<0 or path_id_b>=len(river['osm']['paths']):
        abort(400,'Invalid path ids given')
    river['osm']['paths'][path_id_b].extend(river['osm']['paths'][path_id_a])
    del river['osm']['paths'][path_id_a]
    save_river(river)
    save_transform(['merge_paths_a_after_b',river_id,path_id_a,path_id_b])
    return Response(json.dumps(river), mimetype='application/json')

@application.route('/split_paths/<river_id>/<pathnameslist>')
def split_paths(river_id,pathnameslist):
    try:
        pathnames = pathnameslist.split('^')
    except:
        abort(400,'Cannot parse pathnameslist list')
    river = rivers(river_id)
    if river==None:
        abort(404,'Cannot find river')
    if len(pathnames)!=len(river['osm']['paths']):
        abort(400,"Number of names does't match number of paths")
    i = 0
    for pathname in pathnames:
        print pathnames,pathname,i
        new_river = copy.deepcopy(river)
        new_river['osm']['paths'] = [river['osm']['paths'][i]]
        new_river['_id'] = pathname
        save_river(new_river)
        i += 1
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

