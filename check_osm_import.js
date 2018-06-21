print("# Number of paths histogram #");
print("Number of paths : number of rivers having this number of paths");
cursor=db.getSiblingDB("wwsupdb").osm.aggregate([{"$project":{"_id":0,"nbpaths":{"$size":"$paths"}}},{"$group":{_id:"$nbpaths",number:{$sum:1}}},{"$sort":{_id:1}}])
while(cursor.hasNext()) {o=cursor.next();print(o["_id"]+":\t"+o["number"]);}

