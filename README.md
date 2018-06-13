# wwsupdb
White Water Standup Paddling Database

## Quick start
```
# Clone
git clone https://github.com/fparrel/wwsupdb
cd wwsupdb
# Start MongoDB one instance server
./start_mongod.sh & # Preferably in another terminal
# Get osm data
wget http://download.geofabrik.de/europe/france/corse-latest.osm.pbf
# Build osm data parser
cd pbfparser
cargo build --release
# Insert osm data into MongoDB
./target/release/pbfparser ../corse-latest.osm.pbf
# Scrap eauxvives.org data to a .json file
./scrap_evo.sh
# Match evo and osm data in MongoDB
./match_evo_osm.py
# Compute some length on a river
./len_on_river.py
# Get rivermap.sh public data
rivermap.ch.sh
```
