import re
import utm
import json

extract_coords = re.compile(r"([^\d]*)(\d+)\s(\d+)(.*)") #\s\(\d+\).*")

points = []

geojson_pts = []

f = open('chebro_put_in_egress.txt', 'r')
i = 0
for line in f:
  i += 1
  if i<4:
    continue
  if line.strip()=='':
    continue
  part1,part2 = line.split(':',1)
  s1 = part1.split()
  segment_nb = int(s1[0])
  assert(s1[1]=='Tramo')
  segment_on_river_nb = int(s1[2].strip(':'))
  ((segment_and_river,x,y,obs_and_city),) = extract_coords.findall(part2)
  x = float(x)
  y = float(y)
  s3 = segment_and_river.split()
  river = s3[0]
  segment_name = ' '.join(s3[1:])
  # all points are in UTM grid 30T
  h = 30
  lat,lon = utm.to_latlon(x,y,h,'T')
  pt = {'utmx': x, 'utmy':y, 'lat':lat, 'lon':lon, 'segment_nb':segment_nb,'segment_on_river_nb':segment_on_river_nb,'river':river,'segment_name':segment_name,'desc':obs_and_city}
  points.append(pt)
  #print 'nb=%d tramo_nb=%d river="%s" segment="%s"'%(segment_nb,segment_on_river_nb,river,segment_name)
  geojson_pts.append({ "type": "Feature", "geometry": { "type": "Point", "coordinates": [lon,lat] }, "properties": pt})
f.close()

json.dump(points,open('chebro_put_in_egress.json','w'))
json.dump({"type": "FeatureCollection", "features": geojson_pts }, open('chebro_put_in_egress.geojson','w'))

