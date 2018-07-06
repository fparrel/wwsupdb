# wwsupdb
White Water Standup Paddling Database. Get data from different sources, tries to match them and allow to edit and display the results.

## Current sources

* OSM
* eauxvives.org
* rivermap.ch

## Quick start
### Install stuff. Example for Ubuntu 18.04
```
# Cargo + rust
curl https://sh.rustup.rs -sSf | sh
source $HOME/.cargo/env
# Python flask + flask_babel + gdal + pymongo + scrapy + requests + fuzzywuzzy
sudo apt install python-pip
sudo -H pip install flask flask_babel pymongo scrapy requests fuzzywuzzy matplotlib
sudo apt install python-gdal
sudo apt install mongodb
```
### Use
```
# Clone
git clone https://github.com/fparrel/wwsupdb
cd wwsupdb
# Start MongoDB one instance server
ps -ef | grep mongo # first check if server already running
./start_mongod.sh & # Preferably in another terminal
# Get osm data
mkdir data_osm_pbf
cd data_osm_pbf
#wget http://download.geofabrik.de/europe/france/corse-latest.osm.pbf # this file if you want to quickly test
wget http://download.geofabrik.de/europe/france-latest.osm.pbf # 3Gb file
wget http://download.geofabrik.de/europe/italy-latest.osm.pbf
wget http://download.geofabrik.de/europe/spain-latest.osm.pbf
cd ..
wget http://download.geofabrik.de/europe/france.kml
wget http://download.geofabrik.de/europe/italy.kml
wget http://download.geofabrik.de/europe/spain.kml
## Build osm data parser V1
#cd pbfparser
#cargo build --release
## Insert osm data into MongoDB
#./osm_parse.sh
# Build osm data parser V2
cd osmpbfparser2
cargo build --release # more than 3 min on a core i7
cd ..
# Insert osm data into MongoDB
./osmpbfparser2/target/release/osmpbfparser2 data_osm_pbf/*.osm.pbf # around 30secs/Gb
# Scrap eauxvives.org data to a .json file
./evo_scrap.sh # 2 or 3min
# Import evo data into MongoDB
./evo_import.py # quick
# Scrap rivermap.ch data to a .xml file
./rivermap_scrap.sh # quick
# Import rivermap data into MongoDB
./rivermap_import.py # quick
# Scrap ckfiumi.net data to a .json file
./ckfiumi_scrap.sh # 1 or 2 min
# Import ckfiumi data into MongoDB
./ckfiumi_import.py # quick
# Match evo, rivermap and ckfiumi with osm data in MongoDB
./match_sources_exact.py # 10 seconds
# Check sources matching
./check_match_sources.py # 10 seconds
firefox check_matches/sources.html &
# Reorder rivermap routes on MongoDB
./rivers_merged_sort.py
# Start flask_server on dev
mkdir config
vi config/config.json # must add config in this file
vi config/keysandpwd.json # must add keys and password in this file
./flask_server.py & # Preferably in another terminal
firefox "http://localhost:8080/"
# Compute some length on a river
./len_on_river.py
# Get rivermap.sh public data
./rivermap.ch.sh
# Scrap descente-canyon.org data
./dc_scrap.sh # 4 minutes
# Import it into MongoDB
./dc_import.py # quick
```

