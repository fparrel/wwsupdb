#!/usr/bin/env python

from xml.etree import ElementTree as ET

# Parse xml
rivermap = ET.parse(open("rivermap_ch_scrap.xml","r"))
r = rivermap.getroot()

# Parse sations
stations = {}
for s in r.find('stationen'):
  stations[s.attrib['id']] = s.attrib

# Parse parcours and group them by river
rivers = {}
for a in r.find('abschnitte'):
  parcours = {'name':a.attrib['strecke'],
              'ww_class':a.attrib['ww'],
              'start':{'lat':float(a.attrib['latstart']),'lon':float(a.attrib['lngstart'])},
              'end':{'lat':float(a.attrib['latend']),'lon':float(a.attrib['lngend'])},
              'region':a.attrib['region']
              }
  # unidentified tags
  assert(a.attrib['wertung'] in ('C_LVU', 'C_STU', 'C_MWM', 'C_NWP', 'C_HWU', 'C_NNW', 'C_HWP', 'C_HHW', 'C_NWM', 'C_HWM', 'C_RGU', 'C_MWP', 'C_LV_OLD'))
  assert(a.attrib['typeId'] in ('1','2','3','4'))
  assert(a.attrib['hilfsstation'] in ('0', '1')) # Station is upstream or downstream of route
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
  else:
    print 'no station for',parcours['name'].encode('utf8')
    assert(a.attrib['einheit']=='')
  # add to rivers
  if rivers.has_key(a.attrib['fluss']):
    rivers[a.attrib['fluss']]['route_rivermap'].append(parcours)
  else:
    rivers[a.attrib['fluss']] = {'_id':a.attrib['fluss'],'name':a.attrib['fluss'],'route_rivermap':[]}

# Insert into MongoDB
import pymongo
client = pymongo.MongoClient()
bulk = []
for name,river in rivers.iteritems():
  bulk.append(pymongo.ReplaceOne({'_id':river['_id']},river,upsert=True))
result = client.wwsupdb.rivermap.bulk_write(bulk)
print result.modified_count,result.upserted_count,result.inserted_count,len(rivers),client.wwsupdb.rivermap.count()
# note: return 0,0,0 if no data is modified
