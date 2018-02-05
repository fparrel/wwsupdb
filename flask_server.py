#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Web interface for updating rivers
#


import sys
import json
from flask import Flask,render_template,send_file,Response,flash,request,redirect,session,abort
from flask_babel import Babel,gettext
from serialize_filedump import load_rivers,save_rivers
try:
    from config import keysnpwds
except:
    print 'You must define keysnpwds in config.py'
    exit()


# Create flask application
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = 'uploads'
application.secret_key = keysnpwds['secret_key']


## Internationalization (i18n)

babel = Babel(application)


## Rivers cache

rivers = load_rivers()


## Map

@application.route('/',defaults={'map_type':'GMaps'})
@application.route('/<map_type>')
def index(map_type):
    return render_template('map.html',map_type=map_type,GMapsApiKey=keysnpwds['GMapsApiKey'],GeoPortalApiKey=keysnpwds['GeoPortalApiKey'])

@application.route('/river/<name>')
def river(name):
    return Response(json.dumps(rivers[name]), mimetype='application/json')

@application.route('/river/<river_name>/parcours/<int:parcours_id>/<element>/point/<float:lat>/<float:lon>')
def set_river_element_point(river_name,parcours_id,element,lat,lon):
    rivers[river_name]['parcours'][parcours_id][element+'_point']=(lat,lon)
    return Response('OK')

@application.route('/river/<river_name>/parcours/<int:parcours_id>/<element>/point')
def get_river_element_point(river_name,parcours_id,element):
    if rivers[river_name]['parcours'][parcours_id].has_key(element+'_point'):
        return rivers[river_name]['parcours'][parcours_id][element+'_point']
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

