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
        river = client.wwsupdb.rivers_merged.find_one({"_id":name})
        if river==None:
            river = client.wwsupdb.rivers.find_one({"_id":name})
        return river

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

