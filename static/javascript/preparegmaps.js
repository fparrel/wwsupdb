
var river_paths = [];

const path_color = "#bb8000";
const highlighted_path_color = "red";

function clearMapObjects() {
    var i;
    for(i=0;i<river_paths.length;i++) {
        river_paths[i].setMap(null);
        river_paths = [];
    }
    for(i=0;i<rivermap_markers.length;i++) {
        rivermap_markers[i].setMap(null);
        rivermap_markers = [];
    }
}

function zoomToPath(i) {
    var bounds = new google.maps.LatLngBounds();
    var j;
    for(j=0;j<river_paths[i].getPath().length;j++) {
        bounds.extend(river_paths[i].getPath().getAt(j));
    }
    map.fitBounds(bounds);
}

function highlightPath(span,i) {
    river_paths[i].setOptions({strokeColor: highlighted_path_color});
    span.style.color = highlighted_path_color;
}

function unhighlightPath(span,i) {
    river_paths[i].setOptions({strokeColor: path_color});
    span.style.color = "unset";
}

function addRiverPaths(river_points) {
    var i;
    var j;
    var bounds = new google.maps.LatLngBounds();
    for (i=0;i<river_points.length;i++) {
        river_paths[i] = new google.maps.Polyline(
            {
                path: river_points[i],
                geodesic: true,
                strokeColor: path_color,
                strokeOpacity: 1.0,
                strokeWeight: 4
            });
        river_paths[i].setMap(map);
        for(j=0;j<river_points[i].length;j++) {
            bounds.extend(river_points[i][j]);
        }
    }
    map.fitBounds(bounds);
}

function toogleRiverPath(i,checked) {
    if (checked) {
        river_paths[i].setMap(map);
    } else {
        river_paths[i].setMap(null);
    }
}

/*
// redraw track polyline from contents of river_points
function redrawRiverPaths() {
    var i;
    for(i=0;i<river_paths.length;i++) {
        river_paths[i].setMap(null);
    }
    for (i=0;i<river_points.length;i++) {
        river_paths[i] = new google.maps.Polyline(
            {
                path: river_points[i],
                geodesic: true,
                strokeColor: "#bb8000",
                strokeOpacity: 1.0,
                strokeWeight: 4
            });
        river_paths[i].setMap(map);
    }
}

function addRiverPoints(path_list) {
  var pathi;
  for(pathi=0;pathi<path_list.length;pathi++) {
    var pts = path_list[pathi];
    if (pts.length>0) {
        var i;
        var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(pts[0].lat,pts[0].lon),new google.maps.LatLng(pts[0].lat,pts[0].lon));
        for(i=0;i<pts.length;i++) {
            addRiverPoint(pts[i],pathi,i);
            bounds.extend(new google.maps.LatLng(pts[i].lat,pts[i].lon));
        }
        map.fitBounds(bounds);
        redrawRiverPaths();
    }
  }
}*/

function addPoint(newpt) {
    //current_parcours_id
    //current_deb
    var pt_marker;
    pt_marker = new google.maps.Marker({position: new google.maps.LatLng(newpt.lat, newpt.lon), map: map, draggable: true});
    //var url = '/river/'+current_river+'/parcours/'+current_parcours_id+(current_deb?'/debarquement':'/embarquement')+'/point/'+newpt.lat+'/'+newpt.lon;
    //$.get(url, function() { console.log('done'); } ).fail(function(err){$("#svrresponse").html(err.responseText);});
}

function addPointRivermap(newpt,title) {
    if (!((newpt.lat, newpt.lon) in rivermap_markers)) {
      rivermap_markers[(newpt.lat, newpt.lon)] = new google.maps.Marker({position: new google.maps.LatLng(newpt.lat, newpt.lon), map: map, draggable: true,label:title});
    } else {
      rivermap_markers[(newpt.lat, newpt.lon)].label += title;
    }
}

/*
// Add a given point object to the map
function addRiverPoint(newpt,pathi,index) {
    if(index==0) {
      river_points[pathi]=[];
    }
    river_points[pathi][index] = new google.maps.LatLng(newpt.lat,newpt.lon);
    river_points[pathi][index].pt = newpt;
}
*/

/* Click on map event */
function onMapClick(lat,lon) {
    addPoint(new Point(lat,lon));
}

var rivermap_markers=[];

// Create icons
var sel_icon = "/static/images/MarkerStart.png";
var pt_icon = "/static/images/MarkerSelBegin.png";

// Create map
var mapOptions = {
  zoom: 5,
  center: new google.maps.LatLng(45.0,0.0),
  mapTypeId: google.maps.MapTypeId.TERRAIN
};

var map = new google.maps.Map(document.getElementById("map"),mapOptions);

// Click on map handling
google.maps.event.addListener(map,"click",function(evt) {
    onMapClick(evt.latLng.lat(),evt.latLng.lng());
});

//getRiver("Var");
