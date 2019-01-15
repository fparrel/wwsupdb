#!/usr/bin/env python
# -*- coding: utf8 -*-

from xml.etree import ElementTree as ET

# Hard codes

tomerge = {"Somvixer Rhein":"Rhein","Alter Rhein":"Rhein","Averser Rhein":"Rhein","Medelser Rhein":"Rhein",
           "Rhin Antérieur (Vorderrhein)":"Rhein","Rhin":"Rhein","Rhône / Rotten":"Rhône"}

# end of hard codes


# Parse xml
rivermap = ET.parse(open("rivermap_ch_scrap.xml","r"))
r = rivermap.getroot()

# Parse sations
stations = {}
for s in r.find('stationen'):
  stations[s.attrib['id']] = s.attrib

# Parse parcours and group them by river
rivers = {}
typeid2str = {'1':'section','2':'slalom','3':'playspot','4':'waterfall'}
for a in r.find('abschnitte'):
  parcours = {'name':a.attrib['strecke'],
              'ww_class':a.attrib['ww'],
              'start':{'lat':float(a.attrib['latstart']),'lon':float(a.attrib['lngstart'])},
              'end':{'lat':float(a.attrib['latend']),'lon':float(a.attrib['lngend'])},
              'region':a.attrib['region']
              }
  # unidentified tags
  # level unknown, station unknown, med water med, low water,...?
  assert(a.attrib['wertung'] in ('C_LVU', 'C_STU', 'C_MWM', 'C_NWP', 'C_HWU', 'C_NNW', 'C_HWP', 'C_HHW', 'C_NWM', 'C_HWM', 'C_RGU', 'C_MWP', 'C_LV_OLD'))
  # item type
  parcours['type'] = typeid2str[a.attrib['typeId']]
  # parse length
  assert(a.attrib['luft'][-3:]==' km')
  if a.attrib['luft'][:-3]!='':
    parcours['length'] = float(a.attrib['luft'][:-3])
  else:
    print 'no length for',parcours['name'].encode('utf8')
  # parse ref station
  if a.attrib.has_key('refstation') and len(a.attrib['refstation'])>0:
    parcours['station']=stations[a.attrib['refstation']]
    parcours['water_lvls_kayak']={'unit':a.attrib['einheit']}
    low=float(a.attrib['nw'])
    med=float(a.attrib['mw'])
    high=float(a.attrib['hw'])
    if low!=0.0:
      parcours['water_lvls_kayak']['low']=low
    if med!=0.0:
      parcours['water_lvls_kayak']['low']=med
    if high!=0.0:
      parcours['water_lvls_kayak']['low']=high
    assert(a.attrib['einheit'] in ('cm', u'm\xb3/s'))
    parcours['station_is_indirect'] = (a.attrib['hilfsstation']=='1')
  else:
    print 'no station for',parcours['name'].encode('utf8')
    assert(a.attrib['einheit']=='')
  # add to rivers
  rivername = a.attrib['fluss'].strip()
  new_rivername = tomerge.get(rivername.encode('utf8'))
  if new_rivername!=None:
    rivername = new_rivername
  if rivers.has_key(rivername):
    rivers[rivername]['routes_rivermap'].append(parcours)
  else:
    rivers[rivername] = {'_id':rivername,'name':rivername,'routes_rivermap':[parcours]}

def getNextWpt():
  for rivername,river in rivers.iteritems():
    for route in river['routes_rivermap']:
      yield ('<wpt lat="%f" lon="%f"><name>Start - %s - %s</name></wpt>'%(route['start']['lat'],route['start']['lon'],route['name'],route['ww_class'])).encode('utf8')
      yield ('<wpt lat="%f" lon="%f"><name>End - %s - %s</name></wpt>'%(route['end']['lat'],route['end']['lon'],route['name'],route['ww_class'])).encode('utf8')


i = 0
begin = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">'
out = [begin]
endline = '</gpx>'
NB_WPTS_BY_FILE = 100
for wpt in getNextWpt():
  out.append(wpt)
  if i > 0 and i % NB_WPTS_BY_FILE == 0:
    out.append(endline)
    open('rivermap%d.gpx'%(i/NB_WPTS_BY_FILE),'w').write('\n'.join(out))
    out = [begin]
  i += 1

