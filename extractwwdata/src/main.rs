extern crate osmpbfreader;
extern crate rand;
use std::env::args;
use std::collections::HashMap;
use std::io::Write;
use rand::Rng;

fn is_navigable(v: &String) -> bool {
  let navigable_waterways = ["river", "stream", "canal"];
  navigable_waterways.contains(&&v[0..])
}

pub struct Section {
  pub grade: String,
  pub path: Vec<(f64,f64)>,
  pub put_in: Option<(f64,f64)>,
  pub egress: Option<(f64,f64)>
}

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

fn process_file(input_filename : &String, output_filename : &String) {

  // Open and prepare file parser
  let f = match std::fs::File::open(&std::path::Path::new(input_filename)) {
    Ok(f) => f,
    Err(why) => { println!("Cannot open {}: {}", input_filename, why); return; }
  };
  let mut pbf = osmpbfreader::OsmPbfReader::new(f);

  println!("Parsing {}...", input_filename);

  // Get the objects and dependencies we have interest on
  let objs = pbf.get_objs_and_deps(|obj| {
      (obj.is_way() && obj.tags().contains_key("waterway") && (is_navigable(obj.tags().get("waterway").unwrap()))) ||
      (obj.is_node() && obj.tags().contains_key("whitewater"))
    }).unwrap();

  // Buffer for keeping (lat, lon) from NodeId
  let mut nodes = HashMap::new();

  // Objects we want to retrieve
  let mut egresses = Vec::new();
  let mut put_ins = Vec::new();
  let mut rapids = Vec::new();
  let mut sections = Vec::new();

  println!("Analysing {} objects", objs.len());

  for (_id, obj) in &objs {
    match obj {
      osmpbfreader::OsmObj::Node(n) => {

        // Insert in node buffer for later path resolving
        nodes.insert( n.id, (n.lat(),n.lon()) );

        // Check if it is an egrees, put_in or rapid
        if obj.tags().contains_key("whitewater") {
          let ww: Vec<&str> = obj.tags().get("whitewater").unwrap().split(';').collect();
          if ww.contains(&"egress") {
            egresses.push(n);
          }
          if ww.contains(&"put_in") {
            put_ins.push(n);
          }
        }
        if obj.tags().contains_key("whitewater:rapid_grade") {
          rapids.push(n);
        }

      }
      osmpbfreader::OsmObj::Way(w) => {

        // build path from nodes
        let mut path = Vec::new();
        for node_id in &w.nodes {
          match nodes.get(&node_id) {
            Some(node) => path.push((node.0,node.1)),
            None => { panic!(); }
          }
        }

        // check if it has whitewater data
        if obj.tags().contains_key("whitewater:section_grade") {
          sections.push(Section { grade: obj.tags().get("whitewater:section_grade").unwrap().to_string(),
                                  path, put_in:None, egress:None});
        }

      }
      osmpbfreader::OsmObj::Relation(_) => ()
    }
  }

  println!("nb of rapids: {}", rapids.len());
  println!("nb of egress: {}", egresses.len());
  println!("nb of put_in: {}", put_ins.len());
  println!("nb of sections: {}", sections.len());

  // match put_in / egress / rapids with sections
  for put_in in put_ins {
    let mut closest = sections.iter_mut().min_by_key(|ref section| 
                            dist((put_in.lat(),put_in.lon()), (section.path[0].0, section.path[0].1)).round() as i64);
    match closest {
      Some(mut section) => {
        let d = dist((put_in.lat(),put_in.lon()), (section.path[0].0, section.path[0].1));
        if d < 1000.0 {
          //println!("Section of put_in found at {}m",d.round());
          section.put_in = Some((put_in.lat(), put_in.lon()));
        }
      },
      None => println!("Section of put_in not found")
    }
  }

  for egress in egresses {
    let mut closest = sections.iter_mut().min_by_key(|ref section| 
             dist((egress.lat(),egress.lon()), (section.path.last().unwrap().0, section.path.last().unwrap().1)).round() as i64);
    match closest {
      Some(mut section) => {
        let d = dist((egress.lat(),egress.lon()), (section.path.last().unwrap().0, section.path.last().unwrap().1));
        if d < 1000.0 {
          //println!("Section of egress found at {}m",d.round());
          section.egress = Some((egress.lat(), egress.lon()));
        }
      },
      None => println!("Section of egress not found")
    }
  }

  /*for rapid in rapids {
    
  }*/

  // Connect paths
  let nb_sections_before = sections.len();
  loop {
    // Analyze each section with all the other ones
    for i in 0..sections.len() {
      for j in 0..sections.len() {
        if i != j {
          // If last point of i is first point of j and no put_in nor egress, it mean that j can be merged after i
          if sections[i].egress.is_none() && sections[j].put_in.is_none() && sections[i].path.len()>0 && sections[j].path.len()>0 && 
            sections[i].path.last().unwrap() == sections[j].path.first().unwrap() {
            // We need to use `replace` in order to avoir having two &mut on sections
            let mut path_of_section_j = std::mem::replace(&mut sections[j].path, Vec::new());
            sections[i].path.append(&mut path_of_section_j);
            // Don't forget to copy egress if any
            sections[i].egress = sections[j].egress;
          }
        }
      }
    }
    // Remove the empty sections from vector
    // If the size of vector is still the same that mean that all mergeable paths have been merged
    let old_len = sections.len();
    sections.retain(|section| section.path.len()>0);
    if old_len == sections.len() {
      break
    }
  }
  println!("nb sections: {} -> {}", nb_sections_before, sections.len());

  // Output contents
  let mut fout = match std::fs::File::create(output_filename) {
    Ok(f) => f,
    Err(why) => { println!("Cannot open {}: {}", output_filename, why); return; }
  };
  write!(fout,"{{ \"type\": \"FeatureCollection\", \"features\": [").expect("Write begin");
  let mut section_nb = 0;
  let mut first = true;
  let mut rng = rand::thread_rng();
  for section in sections {
    let color = rng.gen_range(0, 16777215);
    match section.put_in {
      Some(p) => {
        if !first {
          write!(fout, ",").expect("Write comma");
        }
        first = false;
        write!(fout, "\n{{ \"type\": \"Feature\", \"geometry\": {{ \"type\": \"Point\", \"coordinates\": [{}, {}] }}, \
                      \"properties\": {{ \"name\": \"PutIn{}\", \"marker-color\": \"#{:06x}\" }} }}\n", p.1, p.0, section_nb, color)
                                                                                                              .expect("Write put_in");
      },
      None => ()
    }
    if !first {
      write!(fout, ",").expect("Write comma");
    }
    first = false;
    write!(fout, "{{ \"type\": \"Feature\", \"geometry\": {{ \"type\": \"LineString\", \"coordinates\": [").expect("Write path");
    let mut firstpt = true;
    for p in section.path {
      if !firstpt {
        write!(fout, ",").expect("Write comma");
      }
      firstpt = false;
      write!(fout, "[{},{}]", p.1, p.0).expect("Write point");
    }
    write!(fout, "] }}, \"properties\": {{ \"name\": \"Section{}\", \"stroke\": \"#{:06x}\", \"grade\": \"{}\" }} }}",
                                                                               section_nb, color, section.grade).expect("Write path");
    match section.egress {
      Some(p) => {
        // In case we have an egress in from of a put_in, since we cannot handle transparency: put a small marker size
        write!(fout, ",\n{{ \"type\": \"Feature\", \"geometry\": {{ \"type\": \"Point\", \"coordinates\": [{}, {}] }}, \
                      \"properties\": {{ \"name\": \"Egress{}\", \"marker-color\": \"#{:06x}\", \"marker-size\": \"small\" }} }}",
                                                                                  p.1, p.0, section_nb, color).expect("Write egress");
      },
      None => ()
    };
    section_nb += 1;
  }
  write!(fout,"]}}").expect("Write end");
}

fn main() {
  let arg1 = args().nth(1);
  if arg1.is_none() || ["-h", "--help"].contains(&&arg1.unwrap()[..]) {
    println!("Usage: {} input.osm.pbf [output.geojson]",args().nth(0).unwrap());
    return;
  }
  let input_filename = args().nth(1).unwrap();
  let output_filename = match args().nth(2) {
    Some(arg2) => arg2,
    None => String::from("output.geojson")
  };
  process_file(&input_filename, &output_filename);
}

