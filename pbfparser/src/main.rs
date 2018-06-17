extern crate osm_pbf_iter;
extern crate num_cpus;
extern crate serde;
#[macro_use] extern crate serde_derive;
#[macro_use(bson, doc)] extern crate bson;
extern crate mongodb;

use std::env::args;
use std::fs::File;
use std::io::{Seek, SeekFrom};
use std::time::Instant;
use std::sync::mpsc::{sync_channel, SyncSender, Receiver};
use std::thread;
use std::collections::HashMap;
use std::f64;

use osm_pbf_iter::*;
use mongodb::{Client, ThreadedClient};
use mongodb::db::ThreadedDatabase;
use mongodb::coll::options::WriteModel;


type PayLoad = (Vec<(u64,f64,f64)>,Vec<(String,u64,Vec<i64>)>);

// Structure holding a river, used for bson serialization
#[derive(Serialize, Deserialize, Debug)]
pub struct River {
    #[serde(rename = "_id")]  // Use MongoDB's special primary key field name when serializing 
    pub id: String,
    pub paths: Vec< Vec<(f64,f64)> >
}

// Functions kept for future use
/*
fn geodetic_dist_great_circle(lat1:f64,lon1:f64,lat2:f64,lon2:f64) -> f64 {
    //Compute distance between two points of the earth geoid (approximated to a sphere)"
    // convert inputs in degrees to radians
    let lat1_ = lat1 * 0.0174532925199433;
    let lon1_ = lon1 * 0.0174532925199433;
    let lat2_ = lat2 * 0.0174532925199433;
    let lon2_ = lon2 * 0.0174532925199433;
    // just draw a schema of two points on a sphere and two radius and you'll understand
    let a = ((lat2_ - lat1_)/2.0).sin().powi(2) + lat1_.cos() * lat2_.cos() * ((lon2_ - lon1_)/2.0).sin().powi(2);
    6372795.0 * 2.0 * a.sqrt().atan2((1.0-a).sqrt())
}

fn dist(pt1:(f64,f64),pt2:(f64,f64)) -> f64 {
    geodetic_dist_great_circle(pt1.0,pt1.1,pt2.0,pt2.1)
}
*/

fn blobs_worker(req_rx: Receiver<Blob>, res_tx: SyncSender<PayLoad>) {

    let mut nodes = Vec::new();
    let mut rivers = Vec::new();

    loop {
        let blob = match req_rx.recv() {
            Ok(blob) => blob,
            Err(_) => break,
        };

        let data = blob.into_data();
        let primitive_block = PrimitiveBlock::parse(&data);
        for primitive in primitive_block.primitives() {
            match primitive {
                Primitive::Node(node) => {
                    nodes.push((node.id,node.lat,node.lon));
                },
                Primitive::Way(way) => {
                    // Detect rivers with a name
                    let mut name = "";
                    let mut is_river = false;
                    for (k,v) in way.tags() {
                         if k=="name" {
                             name = v;
                         }
                         if k=="waterway" && (v=="river" || v=="stream") {
                             is_river = true;
                         }
                    }
                    if is_river && name != "" {
                        // refs is list of node ids
                        let mut refs = Vec::new();
                        for r in way.refs() {
                             refs.push(r);
                        }
                        rivers.push((String::from(name),way.id,refs));
                    }
                },
                Primitive::Relation(_) => ()
            }
        }
    }

    res_tx.send((nodes,rivers)).unwrap();
}

// Algorithm to merge unordered consecutive paths. Modify argument itself
// Example: [[1,2,3],[5,6],[3,4,5]] -> [[1,2,3,4,5,6]]
fn merge_paths( paths: &mut Vec<Vec<i64>>) {
    let mut old_len = paths.len() + 1;
    while paths.len() < old_len {
        old_len = paths.len();
        let mut b = false;
        for i in 0..paths.len() {
            for j in 0..paths.len() {
                if i != j && paths[i].last().unwrap() == paths[j].first().unwrap() {
                    // merge j into i
                    if i<j {
                        let pj = paths.remove(j);
                        paths[i].extend(pj);
                    } else {
                        let pj = paths.remove(j);
                        paths[i-1].extend(pj); // if j<i that mean that i>0
                    }
                    // We must break because we are changing paths.len()
                    b = true;
                    break;
                }
                if i != j && paths[i].first().unwrap() == paths[j].last().unwrap() {
                    // merge i into j
                    if j<i {
                        let pi = paths.remove(i);
                        paths[j].extend(pi);
                    } else {
                        let pi = paths.remove(i);
                        paths[j-1].extend(pi); // if i<j that mean that j>0
                    }
                    b = true;
                    break;
                }
            }
            if b {
                break;
            }
        }
    }
}


fn main() {
    let cpus = num_cpus::get();

    for arg in args().skip(1) {
    
        // Generates one worker by CPU
        let mut workers = Vec::with_capacity(cpus);
        for _ in 0..cpus {
            let (req_tx, req_rx) = sync_channel(2);
            let (res_tx, res_rx) = sync_channel(0);
            workers.push((req_tx, res_rx));
            thread::spawn(move || {
                blobs_worker(req_rx, res_tx);
            });
        }

        // Send blobs to workers
        println!("Parsing {}", arg);
        let f = File::open(&arg).unwrap();
        let mut reader = BlobReader::new(f);
        let start = Instant::now();

        let mut w = 0;
        for blob in &mut reader {
            let req_tx = &workers[w].0;
            w = (w + 1) % cpus;

            req_tx.send(blob).unwrap();
        }

        let mut ways: HashMap<u64, (String,Vec<i64>)> = HashMap::new();
        let mut nodes = HashMap::new();
        for (req_tx, res_rx) in workers.into_iter() {

            // Retrieve data from workers
            drop(req_tx);
            let (worker_nodes,worker_rivers) = res_rx.recv().unwrap();

            // Fill nodes cache
            for (id,lat,lon) in worker_nodes {
                nodes.insert(id,(lat,lon));
            }

            // Fill rivers by ids
            for (name,id,refs) in worker_rivers {
                let toinsert;
                match ways.get(&id) {
                    Some(way) => {
                        let mut new_refs = Vec::new();
                        new_refs.extend(&way.1);
                        new_refs.extend(refs);
                        toinsert = (name,new_refs);
                    },
                    None => {
                        toinsert = (name,refs);
                    }
                }
                ways.insert(id,toinsert);
            }
        }

        println!("Grouping by river name");

        // Group rivers paths by name
        let mut rivers: HashMap<String, Vec<Vec<i64>> > = HashMap::new();
        for (_id,(name,refs)) in ways {
            let toinsert;
            match rivers.get(&name) {
                Some(paths) => {
                    let mut new_paths = Vec::new();
                    for path in paths {
                        new_paths.push(path.to_vec());
                    }
                    new_paths.push(refs);
                    toinsert = new_paths;                    
                },
                None => {
                    toinsert = [refs].to_vec();
                }
            }
            rivers.insert(name,toinsert);
        }

        println!("Merge, remove loops and match with nodes...");

        // Connect to MongoDB client and select collection
        let client = Client::connect("localhost", 27017).ok().expect("Failed to initialize client.");
        let rivers_coll = client.db("wwsupdb").collection("rivers");
        let mut bulk = Vec::with_capacity(rivers.len());

        for (name,mut ref_lists) in rivers {

            let paths_count_before = ref_lists.len();

            // Concatenate
            merge_paths(&mut ref_lists);

            // Find loops, example: 
            //     /---------\ 
            // ----+         \--+--------    => ----+            +--------
            //     \------------/                   \------------/

            let mut loops = Vec::new();
            for i in 0..ref_lists.len() {
                for j in 0..ref_lists.len() {
                    if i != j {
                        let mut j_has_start_of_i = false;
                        let mut j_has_end_of_i = false;
                        for k in 0..ref_lists[j].len() {
                            if ref_lists[i][0] == ref_lists[j][k] {
                                j_has_start_of_i = true;
                            }
                            if ref_lists[i][ref_lists[i].len()-1] == ref_lists[j][k] {
                                j_has_end_of_i = true;
                            }
                        }
                        if j_has_start_of_i && j_has_end_of_i {
                            //println!("path {} is a loop of {}",i,j);
                            if !loops.contains(&j) {
                                loops.push(i);
                            }
                        }
                    }
                }
            }

            // Match refs with nodes, ignoring loops
            let mut path_list = Vec::new();
            let mut i = 0;
            for ref_list in ref_lists.iter() {
                if !loops.contains(&i) { // ignore loops
                    let mut path = Vec::new();
                    for r in ref_list {
                        match nodes.get(&(*r as u64)) {
                            Some(re) => path.push((re.0,re.1)),
                            None => (),
                        }
                    }
                    path_list.push(path);
                }
                i += 1;
            }

            println!("River {} paths {}->{}",name,paths_count_before,path_list.len());

            // Insert into MongoDB
            let river = River {
                id: name.to_string(),
                paths: path_list
            };

            let serialized_river = bson::to_bson(&river);  // Serialize
            match serialized_river {
                Ok(sr) => {
                    if let bson::Bson::Document(docu) = sr { // Documentize
                        bulk.push(WriteModel::UpdateOne { filter: doc!{"_id": name.to_string()},
                                                          update: doc!{"$set": docu},
                                                          upsert: Some(true) });
                        //bulk.push(WriteModel::InsertOne { document: docu });
                        //bulk.push(docu);
                        if bulk.len()>100 {
                            println!("Insert into db... {}",bulk.len());
                            let result = rivers_coll.bulk_write(bulk.clone(), true);
                            println!("Number of rivers inserted: ins:{} match:{} modif:{} del:{} upset:{}",result.inserted_count,result.matched_count,result.modified_count,result.deleted_count,result.upserted_count);
                            //println!("Write errors: {}",result.bulk_write_exception.unwrap().write_errors.len());
                            match result.bulk_write_exception {
                                Some(exception) => println!("OK: {}",exception.message),
                                None => println!("ERROR")
                            };
                            //rivers_coll.insert_many(bulk.clone(), None).expect("Failed to insert documents.");
                            bulk.clear();
                        }
                    } else {
                        println!("Error converting the BSON object into a MongoDB document");
                    }
                },
                Err(_) => println!("Error serializing the River as a BSON object")
            }
        }

        println!("Insert into db... {}",bulk.len());
        //rivers_coll.insert_many(bulk, None).expect("Failed to insert documents.");
        //println!("result = {}", result);
        let result = rivers_coll.bulk_write(bulk, true); // Insert
        println!("Number of rivers inserted: ins:{} match:{} modif:{} del:{} upset:{}",result.inserted_count,result.matched_count,result.modified_count,result.deleted_count,result.upserted_count);
        match result.bulk_write_exception {
            Some(exception) => println!("OK: {}",exception.message),
            None => println!("ERROR")
        };

        // Get duration
        let stop = Instant::now();
        let duration = stop.duration_since(start);
        let duration = duration.as_secs() as f64 + (duration.subsec_nanos() as f64 / 1e9);
        let mut f = reader.to_inner();
        match f.seek(SeekFrom::Current(0)) {
            Ok(pos) => {
                let rate = pos as f64 / 1024f64 / 1024f64 / duration;
                println!("Processed {} MB in {:.2} seconds ({:.2} MB/s)",
                         pos / 1024 / 1024, duration, rate);
            },
            Err(_) => (),
        }
    }
}
