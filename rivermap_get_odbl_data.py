#!/usr/bin/env python
# -*- coding: utf8 -*-

# Hard codes

tomerge = {"Somvixer Rhein":"Rhein","Alter Rhein":"Rhein","Averser Rhein":"Rhein","Medelser Rhein":"Rhein","Rhin Antérieur (Vorderrhein)":"Rhein","Rhin":"Rhein",
           "Rhône / Rotten":"Rhône"}

import requests

# Get rivermap.ch free date
r = requests.get("https://www.rivermap.ch/public/CC-BY-SA-4.0/extract.json")

# Sections are grouped by river in our db
rivers = {}

for section in r.json()["data"]["sections"]:

  # Get river name, and merge it if needed
  rivername = section["river"].strip()
  new_rivername = tomerge.get(rivername.encode('utf8'))
  if new_rivername!=None:
    rivername = new_rivername

  if section.has_key("spotGrades"):
    ww_class = section["generalGrade"] + section["spotGrades"]
  else:
    ww_class = section["generalGrade"]
  if section.has_key('latend') and section.has_key('lngend'):
    e = {'lat':section["latend"],'lon':section["lngend"]}
  else:
    e = None
    print 'No end for section %s'%section['id']
  parcours = {'name':section["section"],
              'ww_class':ww_class,
              'start':{'lat':section["latstart"],'lon':section["lngstart"]},
              'end':e,
              'type':section["type"],
              'region':section["country"]}
  # TODO: length, station
  if section.has_key('calibration'):
    parcours["water_lvls_kayak"] = {"unit":section["calibration"]["units"]}
    if section["calibration"].has_key("lw") and section["calibration"]["lw"] != None:
      parcours['water_lvls_kayak']["low"] = float(section["calibration"]["lw"])
    if section["calibration"].has_key("hw") and section["calibration"]["hw"] != None:
      parcours['water_lvls_kayak']["high"] = float(section["calibration"]["hw"])
    if section["calibration"].has_key("mw") and section["calibration"]["mw"] != None:
      parcours['water_lvls_kayak']["med"] = float(section["calibration"]["mw"])

  # Create new river if needed
  if rivers.has_key(rivername):
    rivers[rivername]['routes_rivermap'].append(parcours)
  else:
    rivers[rivername] = {'_id':rivername,'name':rivername,'routes_rivermap':[parcours]}

# Insert into MongoDB

import pymongo

client = pymongo.MongoClient()
bulk = []
for name,river in rivers.iteritems():
  bulk.append(pymongo.ReplaceOne({'_id':river['_id']},river,upsert=True))

result = client.wwsupdb.rivermap.bulk_write(bulk)
print result.modified_count,result.upserted_count,result.inserted_count,len(rivers),client.wwsupdb.rivermap.count()
# note: return 0,0,0 if no data is modified

