import json
js=json.load(open('eauxvives_org.json','r'))
json.dump(js,open('eauxvives_org-pretty.json','w'),indent=2)
js=json.load(open('osm_rivers.json','r'))
json.dump(js,open('osm_rivers-pretty.json','w'),indent=2)
