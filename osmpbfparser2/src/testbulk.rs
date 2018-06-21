
// Cargo.toml extract:
//
// [dependencies]
// bson = "0.10"
// mongodb = "0.3.7"

#[macro_use(bson, doc)] extern crate bson;
extern crate mongodb;
use mongodb::coll::options::WriteModel;
use mongodb::{Client, ThreadedClient};
use mongodb::db::ThreadedDatabase;
use std::mem;

fn main() {

    // Connect to MongoDB and select collection
    let client = Client::connect("localhost", 27017).ok().expect("Failed to initialize client.");
    let coll = client.db("test").collection("mycol");

    // Make the bulk vector
    let mut bulk = Vec::new();
    for i in 0..1000 {

        // Append a item to the bulk
        bulk.push(WriteModel::UpdateOne { filter: doc!{"_id": i},
                                          update: doc!{"$set" => {"hello" => "world"}},
                                          upsert: Some(true) });

        // Each 11 items, flush bulk
        if bulk.len() > 10 {
            println!("Upsert {} docs into collection...",bulk.len());

            let mut bulk2 = Vec::new(); // create new empty bulk
            mem::swap(&mut bulk, &mut bulk2); // bulk <-> bulk2
            let result = coll.bulk_write(bulk2, true);  // send full bulk

            //let result = coll.bulk_write(bulk.clone(), true); // Unoptimal: bulk cloned
            //let result = coll.bulk_write(bulk, true); // E0382: use after move
            //let result = coll.bulk_write(&bulk, true); // E0308: expected struct `std::vec::Vec`, found reference 

            // Check result
            match result.bulk_write_exception {
                Some(exception) => {
                    if exception.message.len()>0 {
                        println!("ERROR: {}",exception.message);
                    }
                }
                None => ()
            }
            //bulk.clear(); // bulk is now a new empty bulk, clear is unecessary
        } // Compiler will drop bulk2 (the full bulk) at this point
    }

    // Final flush
    if bulk.len() > 0 {
        println!("Upsert {} docs into collection...",bulk.len());
        let result = coll.bulk_write(bulk, true); // No clone nor swap needed here
        match result.bulk_write_exception {
            Some(exception) => {
                if exception.message.len()>0 {
                    println!("ERROR: {}",exception.message);
                }
            }
            None => ()
        }
    }
}
