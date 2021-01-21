extern crate osmpbfreader;
extern crate serde;
#[macro_use] extern crate serde_derive;
#[macro_use(bson, doc)] extern crate bson;
extern crate mongodb;

use std::collections::HashMap;
use std::env::args;
use mongodb::coll::options::WriteModel;
use mongodb::{Client, ThreadedClient};
use mongodb::db::ThreadedDatabase;
use std::mem;

// Structure holding a river, used for bson serialization
#[derive(Serialize, Deserialize, Debug)]
pub struct River {
    pub paths: Vec<(f64,f64)>
}

fn process_file(filename : &String, rivers_coll : &mongodb::coll::Collection) {
    let r = std::fs::File::open(&std::path::Path::new(filename)).unwrap();
    println!("Parsing {:?}...",filename);
    let mut pbf = osmpbfreader::OsmPbfReader::new(r);
    let objs = pbf.get_objs_and_deps(|obj| {
        obj.is_way() && obj.tags().contains_key("waterway") && ( obj.tags().get("waterway").unwrap()=="river" || obj.tags().get("waterway").unwrap()=="stream" || obj.tags().get("waterway").unwrap()=="canal" ) && obj.tags().contains_key("name") && obj.tags().get("name").unwrap().len()>0
    }).unwrap();
    println!("Objs got");
    let mut nodes = HashMap::new();
    let mut bulk = Vec::new();

    for (_id, obj) in &objs {
        match obj {
            osmpbfreader::OsmObj::Node(n) => {
                nodes.insert( n.id, (n.lat(),n.lon()) );
            }
            osmpbfreader::OsmObj::Way(w) => {
                let mut path = Vec::new();
                for node_id in &w.nodes {
                    match nodes.get(&node_id) {
                        Some(node) => path.push((node.0,node.1)),
                        None => { panic!(); }
                    }
                }
                // Insert into MongoDB
                let river = River {
                    paths: path
                };
                let names : Vec<String> = obj.tags().iter().filter(|tag| tag.0.starts_with("name:")).map(|tag| tag.1.clone()).collect();

                let serialized_river = bson::to_bson(&river);  // Serialize
                match serialized_river {
                    Ok(sr) => {
                        if let bson::Bson::Document(docu) = sr { // Documentize
                            bulk.push(WriteModel::UpdateOne { filter: doc!{"_id": obj.tags().get("name").unwrap().to_string()},
                                                              update: doc!{"$push": docu, "$addToSet": {"names": {"$each": bson::to_bson(&names).unwrap()}}},
                                                              upsert: Some(true) });
                            if bulk.len()>100 {
                                println!("Insert into db... {}",bulk.len());
                                let mut bulk2 = Vec::new(); // create new empty bulk
                                mem::swap(&mut bulk, &mut bulk2); // bulk <-> bulk2
                                let result = rivers_coll.bulk_write(bulk2, true); // send full bulk

                                println!("Number of rivers inserted: ins:{} match:{} modif:{} del:{} upset:{}",result.inserted_count,result.matched_count,result.modified_count,result.deleted_count,result.upserted_count);
                                match result.bulk_write_exception {
                                    Some(exception) => {
                                        if exception.message.len()>0 {
                                            println!("ERROR: {}",exception.message);
                                        }
                                    }
                                    None => ()
                                }
                                //bulk.clear(); // bulk is now a new empty bulk thanks to swaping, clear is unecessary
                            } // Compiler will drop bulk2 (the full bulk) at this point
                        } else {
                            println!("Error converting the BSON object into a MongoDB document");
                        }
                    },
                    Err(_) => println!("Error serializing the River as a BSON object")
                }
            },
            osmpbfreader::OsmObj::Relation(_) => ()
        }
    }
    if bulk.len()>0 {
        println!("Insert into db... {} river(s)",bulk.len());
        let result = rivers_coll.bulk_write(bulk, true); // send remaining bulk
        println!("Number of rivers inserted: match:{} ins:{} modif:{} del:{} upsert:{}",result.matched_count,result.inserted_count,result.modified_count,result.deleted_count,result.upserted_count);
        match result.bulk_write_exception {
            Some(exception) => {
                if exception.message.len()>0 {
                    println!("ERROR(s): {}",exception.message);
                }
            }
            None => ()
        }
    }

}

fn main() {
    // Connect to MongoDB client and select collection
    let client = Client::connect("localhost", 27017).ok().expect("Failed to initialize client.");
    let rivers_coll = client.db("wwsupdb").collection("osm");
    match rivers_coll.drop() {
        Ok(_) => println!("Collection droped"),
        Err(_) => panic!()
    }
    for arg in args().skip(1) {
        process_file(&arg, &rivers_coll);
    }
}
