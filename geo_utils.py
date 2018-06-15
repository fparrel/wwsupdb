
# Some utilities to work on geo data (lat,lon) and on paths

from math import sin,cos,atan2,sqrt

def GeodeticDistGreatCircle(lat1,lon1,lat2,lon2):
  "Compute distance between two points of the earth geoid (approximated to a sphere)"
  # convert inputs in degrees to radians
  lat1 = lat1 * 0.0174532925199433
  lon1 = lon1 * 0.0174532925199433
  lat2 = lat2 * 0.0174532925199433
  lon2 = lon2 * 0.0174532925199433
  # just draw a schema of two points on a sphere and two radius and you'll understand
  a = sin((lat2 - lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
  c = 2 * atan2(sqrt(a), sqrt(1-a))
  # earth mean radius is 6371 km
  return 6372795.0 * c

def dist(pt1,pt2):
  "Compute distance between two points in form of tuples of (lat,lon)"
  return GeodeticDistGreatCircle(pt1[0],pt1[1],pt2[0],pt2[1])

def len_of_path(path):
  "Compute length of a path given in form of array of tuples of (lat,lon)"
  l = 0.0
  for i in range(0,len(path)-1):
    l += dist(path[i],path[i+1])
  return l

def ids_on_path(a,b,path,threshold=1000):
  "Get the closest 2 points on a path given in form of array of tuples of (lat,lon)"
  # units: meters
  min_dist_a = 6000000 # More than 6000km is almost impossible on Earth
  min_dist_b = 6000000
  i=0
  for pt in path:
    d = dist(a,pt)
    if d<min_dist_a:
      min_dist_a = d
      i_a = i
    d = dist(b,pt)
    if d<min_dist_b:
      min_dist_b = d
      i_b = i
    i += 1
  #print i_a,i_b,min_dist_a,min_dist_b
  if min_dist_a<threshold and min_dist_b<threshold:
    return i_a,i_b
  else:
    return -1,-1

def len_btw_2pts(a,b,path):
  "Compute length on a path given in form of array of tuples of (lat,lon), between the 2 closest points"
  i_a,i_b = ids_on_path(a,b,path)
  if i_a==-1 or i_b==-1:
    raise Exception("Points too far from path")
  if not(i_a<i_b):
    raise Exception("Input points must be given in the descending order")
  return len_of_path(path[i_a:i_b])

def link_paths(paths_in):
  initial_len = sum(map(len,paths_in))
  for i in range(0,len(paths_in)):
    for j in range(0,len(paths_in)):
      if i!=j and len(paths_in[i])>0 and len(paths_in[j])>0 and paths_in[j][0] == paths_in[i][-1]:
        paths_in[i] += paths_in[j]
        paths_in[j] = []
      elif i!=j and len(paths_in[i])>0 and len(paths_in[j])>0 and paths_in[i][0] == paths_in[j][-1]:
        paths_in[j] += paths_in[i]
        paths_in[i] = []
  paths = filter(lambda path:len(path)>0,paths_in)
  assert(initial_len==sum(map(len,paths)))
  #print len(paths)
  return paths
