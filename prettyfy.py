import json
#js=json.load(open('eauxvives_org.json','r'))
#json.dump(js,open('eauxvives_org-pretty.json','w'),indent=2)
#js=json.load(open('osm_rivers.json','r'))
#json.dump(js,open('osm_rivers-pretty.json','w'),indent=2)
#js=json.load(open('eauxvives_org2.json','r'))
#json.dump(js,open('eauxvives_org2-pretty.json','w'),indent=2)

js=json.load(open('eauxvives_org.json','r'))
json.dump(js[:1],open('eauxvives_org-first-pretty.json','w'),indent=2)
#js=json.load(open('osm_rivers_06.json','r'))
#json.dump(js,open('osm_rivers_06-pretty.json','w'),indent=2)
