
// list of points object, map_type dependant
// fields:
//  .pt_index
//  .pt
var river_points = [];

var current_parcours_id;
var current_deb; // debarquement (1) ou embarquement (0)

var current_river_obj;


/* Creates a point object */
function Point(lat,lon,previous_pt) {
    this.lat = lat; // latitude  in decimal degrees
    this.lon = lon; // longitude in decimal degrees
    //[optional] ele : elevation in m
    //[optional] elelbl : elevation label
    if(typeof(previous_pt)=='undefined') {
        this.dist = 0.0;
    }
    else {
        //console.log('plat='+previous_pt.lat); 
        this.dist = previous_pt.dist + geodeticDist(previous_pt.lat,previous_pt.lon,lat,lon);
    }
    //console.log('thisdist='+this.dist);
}

function getRiver(name) {
    $.getJSON('/river/'+name, loadRiverToMap).fail(function(err){$("#svrresponse").html(err.responseText);});
}

function nextRiver(name) {
    console.log('nextRiver');
}

function prevRiver(name) {
    console.log('prevRiver');
}

function setEmbDeb(elem,river,parcours_id,deb) {
    $(".emb_deb").css("color","black");
    elem.style.color = 'red';
    current_parcours_id=parcours_id;
    current_deb=deb;
    console.log('setEmbDeb(%s,%d,%d)',river,parcours_id,deb);
}

function setEmb(elem,river,parcours_id) {
    setEmbDeb(elem,river,parcours_id,0);
}
function setDeb(elem,river,parcours_id) {
    setEmbDeb(elem,river,parcours_id,1);
}

function save() {
    $.get('/flush',function(){$("#svrresponse").html('OK');}).fail(function(err){$("#svrresponse").html(err.responseText);});
}

function search_river(evt,river_name) {
    if(evt.keyCode==13) { // Enter
        getRiver(river_name);
    }
    else if(evt.keyCode==40) { // Down
        nextRiver(river_name);
    }
    else if(evt.keyCode==38) { // Up
        prevRiver(river_name);
    }
}

function selPathsChange() {
    var i;
    var sel=$('input[name=paths_sel]');
    for(i=0;i<sel.length;i++) {
        toogleRiverPath(i,sel[i].checked);
    }
}

function splitPaths() {
    if ($('#split_btn').attr('value')==='Apply split') {
        var i;
        var sel=$('input[name=paths_sel]');
        var names=[];
        for(i=0;i<sel.length;i++) {
            names.push($('#path'+i+'_name').val());
        }
        console.log("names=%o",names);
        $.getJSON('/split_paths/'+current_river_obj._id+'/'+names.join('^'),
                    function(river_obj){
                        $("#svrresponse").html('OK');
                        clearRiverPaths();
                        $("#river_name_input").attr('value','');
                    }).fail(function(err){$("#svrresponse").html(err.responseText);});
    } else {
        var i;
        var sel=$('input[name=paths_sel]');
        var html='';
        for(i=0;i<sel.length;i++) {
            html += 'Path'+i+'<input type="text" id="path'+i+'_name" name="path'+i+'_name" value="'+current_river_obj._id+'"/>';
        }
        $('#split_btn').attr('value','Apply split');
        $('#split_names').html(html);
    }
}

function removeUnselectedPaths() {
    var i;
    var sel=$('input[name=paths_sel]');
    to_remove_list = [];
    for(i=0;i<sel.length;i++) {
        if (!sel[i].checked) {
            to_remove_list.push(i);
        }
    }
    $.getJSON('/remove_paths/'+current_river_obj._id+'/'+to_remove_list.join(','),
                function(river_obj){
                    $("#svrresponse").html('OK');
                    loadRiverToMap(river_obj);
                }).fail(function(err){$("#svrresponse").html(err.responseText);});
}

function mergeSelectedPaths() {
    var i;
    var sel=$('input[name=paths_sel]');
    var to_merge_list = [];
    for(i=0;i<sel.length;i++) {
        if (sel[i].checked) {
            to_merge_list.push(i);
        }
    }
    console.log("to_merge_list=%o",to_merge_list);
    
    if(to_merge_list.length!=2) {
        $("#svrresponse").html('Error: Can only merge two paths');
    } else {
        // Try to merge consecutive paths
        var d1 = geodeticDist(current_river_obj.osm.paths[to_merge_list[0]][0][0],
                            current_river_obj.osm.paths[to_merge_list[0]][0][1],
                            current_river_obj.osm.paths[to_merge_list[1]][current_river_obj.osm.paths[to_merge_list[1]].length-1][0],
                            current_river_obj.osm.paths[to_merge_list[1]][current_river_obj.osm.paths[to_merge_list[1]].length-1][1]);
        var d2 = geodeticDist(current_river_obj.osm.paths[to_merge_list[1]][0][0],
                            current_river_obj.osm.paths[to_merge_list[1]][0][1],
                            current_river_obj.osm.paths[to_merge_list[0]][current_river_obj.osm.paths[to_merge_list[0]].length-1][0],
                            current_river_obj.osm.paths[to_merge_list[0]][current_river_obj.osm.paths[to_merge_list[0]].length-1][1]);
        console.log('d1='+d1+' d2='+d2);
        if ((d1>1000)&&(d2>1000)) {
            $("#svrresponse").html('Error: Paths are more than 1km one from another');
        } else {
            if (d1<d2) {
                $.getJSON('/merge_paths_a_after_b/'+current_river_obj._id+'/'+to_merge_list[0]+'/'+to_merge_list[1],
                            function(river_obj){
                                $("#svrresponse").html('OK');
                                loadRiverToMap(river_obj);
                            }).fail(function(err){$("#svrresponse").html(err.responseText);});                
            } else {
                $.getJSON('/merge_paths_a_after_b/'+current_river_obj._id+'/'+to_merge_list[1]+'/'+to_merge_list[0],
                            function(river_obj){
                                $("#svrresponse").html('OK');
                                loadRiverToMap(river_obj);
                            }).fail(function(err){$("#svrresponse").html(err.responseText);});                
            }
        }
    }
    /*
    var j;
    var to_merge_commands = [];
    while(1) {
        // Get closest paths
        var min_d = 1000;
        var min_a = -1;
        var min_b = -1;
        for(i=0;i<to_merge_list.length;i++) {
            for(j=0;j<to_merge_list.length;j++) {
                console.log("%o %o %o",current_river_obj.osm.paths,to_merge_list,i);
                //to_merge_list is bijective
                if ((i!=j)&&(typeof(current_river_obj.osm.paths[to_merge_list[i]]!=='undefined'))&&(typeof(current_river_obj.osm.paths[to_merge_list[j]]!=='undefined'))) {
                    var d = geodeticDist(current_river_obj.osm.paths[to_merge_list[i]][0][0],
                                        current_river_obj.osm.paths[to_merge_list[i]][0][1],
                                        current_river_obj.osm.paths[to_merge_list[j]][current_river_obj.osm.paths[to_merge_list[j]].length-1][0],
                                        current_river_obj.osm.paths[to_merge_list[j]][current_river_obj.osm.paths[to_merge_list[j]].length-1][1]);
                    if (d<min_d) {
                        min_d = d;
                        min_a = to_merge_list[i];
                        min_b = to_merge_list[j];
                    }
                }
            }
        }
        if (min_d<1000) {
            current_river_obj.osm.paths[min_b].push.apply(current_river_obj.osm.paths[min_b], current_river_obj.osm.paths[min_a]);
            delete current_river_obj.osm.paths[min_a];
            to_merge_commands.push([min_a,min_b]);
            to_merge_list.splice(
        }
        else {
            break;
        }
    }
    var nbpaths_of_to_merge_list = 0;
    for(i=0;i<nbpaths_of_to_merge_list.length;i++) {
        if (typeof(current_river_obj.osm.paths[to_merge_list[i]]!=='undefined')) {
            nbpaths_of_to_merge_list += 1;
        }
    }
    if (nbpaths_of_to_merge_list==1) {
        console.log(to_merge_commands);
    } else {
        $("#svrresponse").html('Cannot find consecutive paths in selected list');
    }*/
}

function loadRiverToMap(river_obj) {
    console.log(river_obj);
    clearRiverPaths();
    current_river_obj = river_obj;

    // Names
    $("#river_name_evo").html('name_evo' in river_obj?(river_obj['name_evo']+' ('+river_obj.evo.length+')'):'/');
    $("#river_name_rivermap").html('name_rivermap' in river_obj?(river_obj['name_rivermap']+' ('+river_obj.rivermap.length+')'):'/');
    $("#river_name_ckfiumi").html('name_ckfiumi' in river_obj?(river_obj['name_ckfiumi']+' ('+river_obj.ckfiumi.length+')'):'/');

    // OSM
    river_points = [];
    var i;
    var j;
    var pts=[];
    var pathshtml='';
    for(i=0;i<river_obj.osm.paths.length;i++) {
        pathshtml += ' <input type="checkbox" name="paths_sel" value="path'+i+'" onclick="selPathsChange();" checked> Path #'+i;
        pts[i]=[];
        for(j=0;j<river_obj.osm.paths[i].length;j++) {
            pts[i][j] = {"lat": river_obj.osm.paths[i][j][0], "lng": river_obj.osm.paths[i][j][1], "lon": river_obj.osm.paths[i][j][1]};
        }
    }
    pathshtml += '<input type="button" value="Merge selected" onclick="mergeSelectedPaths();"> <input type="button" value="Remove unselected" onclick="removeUnselectedPaths();">  <input type="button" id="split_btn" value="Split all" onclick="splitPaths();"><span id="split_names"></span>';
    $("#paths").html(pathshtml);
    addRiverPaths(pts);

    // Evo
    if ("evo" in river_obj) {
        if ("presentation" in river_obj.evo[0]) {
          $("#presentation").html(river_obj.evo[0].presentation);
        }
        if ("parcours" in river_obj.evo[0]) {
          var i=-1;
          $("#parcours").html('<ul><li>'+river_obj.evo[0].parcours.map(function(p) { i++; return p.name + ' (' + p.cotation + ',' + p.duree + ')' + '<ul><li onClick="setEmb(this,\''+river_obj['name']+'\','+i+');" class="emb_deb">Emb:'+p.embarquement+'</li><li onClick="setDeb(this,\''+river_obj['name']+'\','+i+');" class="emb_deb">Deb:'+p.debarquement+'</li></ul>'; }).join('</li><li>')+'</li></ul>');
        } else {
          $("#parcours").html('<b>No parcours in db</b>');
        }
    }

    // RiverMap
    if ("rivermap" in river_obj) {
        if ("routes_rivermap" in river_obj.rivermap[0]) {
          var i=-1;
          $("#routes_rivermap").html('<ul><li>'+river_obj.rivermap[0].routes_rivermap.map(function(p) { i++; return ''+i+': ' +p.name + ': ' + p.length + ' km '+p.ww_class }).join('</li><li>')+'</li></ul>');
          for(i=0;i<river_obj.rivermap[0].routes_rivermap.length;i++) {
              addPointRivermap(river_obj.rivermap[0].routes_rivermap[i].start,'S'+i);
              addPointRivermap(river_obj.rivermap[0].routes_rivermap[i].end,'E'+i);
          }
        } else {
          $("#rivermap").html('<b>No routes in db</b>');
        }
    }
}
