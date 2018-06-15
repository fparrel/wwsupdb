# wwsupdb
White Water Standup Paddling Database. Get data from different sources, tries to match them and allow to edit and display the results.

## Current sources

* OSM
* eauxvives.org
* rivermap.ch

## Quick start
```
# Clone
git clone https://github.com/fparrel/wwsupdb
cd wwsupdb
# Start MongoDB one instance server
./start_mongod.sh & # Preferably in another terminal
# Get osm data
mkdir data_osm_pbf
cd data_osm_pbf
wget http://download.geofabrik.de/europe/france/corse-latest.osm.pbf
# Build osm data parser
cd pbfparser
cargo build --release
# Insert osm data into MongoDB
./osm_parse.sh
# Scrap eauxvives.org data to a .json file
./evo_scrap.sh
# Import evo data into MongoDB
./evo_import.py
# Scrap rivermap.ch data to a .xml file
./rivermap_scrap.sh
# Import rivermap data into MongoDB
./rivermap_import.py
# Scrap ckfiumi.net data to a .json file
./ckfiumi_scrap.sh
# Import ckfiumi data into MongoDB
./ckfiumi_import.py
# Match evo and osm data in MongoDB
./match_evo_osm.py
# Check sources matching
./check_match_sources.py > sources.html
firefox sources.html &
# Reorder rivermap routes on MongoDB
./rivers_merged_sort.py
# Start flask_server on dev
./flask_server.py & # Preferably in another terminal
firefox "http://localhost:8080/"
# Compute some length on a river
./len_on_river.py
# Get rivermap.sh public data
rivermap.ch.sh
```
