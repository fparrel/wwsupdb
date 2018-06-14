
/* redraw track polyline from contents of river_points */
function redrawRiverLine() {
  var pathi;
  if (typeof line != "undefined") {
      var i;
      for(i=0;i<line.length;i++)
        line[i].setMap(null);
  } else {
    line = [];
  }
  for(pathi=0;pathi<river_points.length;pathi++) {
    if(noline)return;
    line[pathi] = new google.maps.Polyline(
        {
            path: river_points[pathi],
            geodesic: true,
            strokeColor: "#bb8000",
            strokeOpacity: 1.0,
            strokeWeight: 4
        });
    line[pathi].setMap(map);
  }
}

/* remove all markers */
function removeMarkers() {
    var i;
    for(i=0;i<markers.length;i++) {
        markers[i].setMap(null);
    }
    markers = [];
}

function removeMarker(index) {
    markers[index].setMap(null);
}

function addPoint(newpt) {
    //current_parcours_id
    //current_deb
    var pt_marker;
    pt_marker = new google.maps.Marker({position: new google.maps.LatLng(newpt.lat, newpt.lon), map: map, draggable: true});
    var url = '/river/'+current_river+'/parcours/'+current_parcours_id+(current_deb?'/debarquement':'/embarquement')+'/point/'+newpt.lat+'/'+newpt.lon;
    $.get(url, function() { console.log('done'); } ).fail(function(err){$("#svrresponse").html(err.responseText);});
}

var rivermap_markers=[];
function addPointRivermap(newpt,title) {
    if (!((newpt.lat, newpt.lon) in rivermap_markers)) {
      rivermap_markers[(newpt.lat, newpt.lon)] = new google.maps.Marker({position: new google.maps.LatLng(newpt.lat, newpt.lon), map: map, draggable: true,label:title});
    } else {
      rivermap_markers[(newpt.lat, newpt.lon)].label += title;
    }
}

/* Add a given point object to the map */
function addRiverPoint(newpt,pathi,index) {
    if(index==0) {
      river_points[pathi]=[];
    }
    river_points[pathi][index] = new google.maps.LatLng(newpt.lat,newpt.lon);
    river_points[pathi][index].pt = newpt;
}

/* Click on map event */
function onMapClick(lat,lon) {
    addPoint(new Point(lat,lon));
}

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

function addRiverPoints(path_list) {
  var pathi;
  for(pathi=0;pathi<path_list.length;pathi++) {
    //console.log("path#"+pathi);
    var pts = path_list[pathi];
    //console.log("pts="+pts);
    if (pts.length>0) {
        var i;
        var bounds = new google.maps.LatLngBounds(new google.maps.LatLng(pts[0].lat,pts[0].lon),new google.maps.LatLng(pts[0].lat,pts[0].lon));
        for(i=0;i<pts.length;i++) {
            addRiverPoint(pts[i],pathi,i);
            bounds.extend(new google.maps.LatLng(pts[i].lat,pts[i].lon));
        }
        map.fitBounds(bounds);
        redrawRiverLine();
        refreshRiverLength();
    }
  }
}

getRiver("Var");
