
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

// list of points object, map_type dependant
// fields:
//  .pt_index
//  .pt
var river_points = [];

// list of markers for easy remove
var markers = [];

/* ask elevation to the server for a given point */
function askElevation(pt) {
    /*var client = new XMLHttpRequest();
    client.pt = pt;
    client.open('GET','/ele/'+pt.lat+'/'+pt.lon);
    client.send();
    client.onreadystatechange = onGetEleAnswer;*/
}

/* When server answer to a get elevation request */
function onGetEleAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            this.pt.elelbl.innerHTML = this.responseText+'m';
            this.pt.ele = parseInt(this.responseText);
            refreshLength();
            refreshGraph();
        }
    }
}

function computePathLengthAndEleDiff(points) {
    var i;
    var d;
    var l = 0;
    var dminus = 0;
    var dplus = 0;
    /*for(i=1;i<points.length;i++) {
        l += geodeticDist(points[i-1].pt.lat,points[i-1].pt.lon,points[i].pt.lat,points[i].pt.lon);
        points[i].pt.dist = l;
        if ((typeof points[i].pt.ele != "undefined")&&(typeof points[i-1].pt.ele != "undefined")) {
            d = points[i].pt.ele-points[i-1].pt.ele;
            if(d>0) dplus += d;
            else dminus += -d;
        }
    }*/
    return [l,dplus,dminus];
}

function refreshRiverLength() {
    var res = computePathLengthAndEleDiff(river_points);
    document.getElementById('length').innerHTML = res[0].toFixed(0)+" m";
    document.getElementById('dplus').innerHTML = res[1].toFixed(0)+" m";
    document.getElementById('dminus').innerHTML = res[2].toFixed(0)+" m";
}

var maptypes=["GMaps","GeoPortal"];

var eles;
var dists;
var marginsize;
var pt2px;
var ptinput2px=null;

var selxPt=-1;
var selxLeft=-1;
var selxRight=-1;
var noline=0;

function ptIndexFromPosx(posx) {
    if(posx<marginsize)
        return -1;
    var i;
    for(i=0;i<pt2px.length;i++) {
        if(posx<=pt2px[i]+marginsize)
            return i;
    }
    return -1;
    /*
    posx = posx - marginsize + 1;
    var r = Math.round(posx * eles.length / (800-marginsize-30));
    if(r<0) return -1;
    if(r>399) return -1;
    return r;*/
}
function posxFromPtIndex(i) {
    //return marginsize + Math.round(i * (800-marginsize-30) / eles.length) + 11;
    return pt2px[i]+marginsize+9;
}

function refreshSelInfos(up) {
    var i1 = ptIndexFromPosx(selxLeft);
    var i2 = ptIndexFromPosx(selxRight);
    var i0 = ptIndexFromPosx(selxPt);
    var profile_infos = "";
    var curpt_infos = "";
    //alert(i0+" "+i1+" "+i2);
    if((i1!=-1)&&((i2!=-1)||(!up))) {
        document.getElementById("markerleft").style.left = posxFromPtIndex(i1) + "px";
        document.getElementById("markerleft").style.display = "inline";
    }
    else {
        document.getElementById("markerleft").style.display = "none";
    }
    if((i1!=-1)&&(i2!=-1)) {
        document.getElementById("markerright").style.left = (posxFromPtIndex(i2) - 10)+ "px";
        document.getElementById("markerright").style.display = "inline";
        var hdist = (dists[i2]-dists[i1]);
        var vdist = (eles[i2]-eles[i1]);
        profile_infos += "<b>"+SELECTION+"</b><br/>"+DIST+Math.round(hdist)+"m<br/>"+VERT_DST+Math.round(vdist)+"m";
        if(hdist>0) {
            var slope = vdist * 100.0 / hdist;
            profile_infos += "<br/>"+SLOPE+Math.round(slope)+"% "+Math.round(Math.atan(vdist/hdist)*180/Math.PI)+"&deg;";
        }
    }
    else {
        document.getElementById("markerright").style.display = "none";
    }
    if(i0!=-1) {
        document.getElementById("markerpt").style.left = posxFromPtIndex(i0) + "px";
        //document.getElementById("markerpt").style.left = "100px";
        document.getElementById("markerpt").style.display = "inline";
        curpt_infos += "<b>"+CURRENT_POINT+"</b><br/>"+ELE+eles[i0]+"m";
        if(i0<eles.length-1) {
            var hdist = (dists[i0+1]-dists[i0]);
            var vdist = (eles[i0+1]-eles[i0]);
            if(hdist>0) {
                var slope = vdist * 100.0 / hdist;
                curpt_infos += "<br/>"+SLOPE+Math.round(slope)+"% "+Math.round(Math.atan(vdist/hdist)*180/Math.PI)+"&deg;";
            }
        }
        //curpt_infos += i0;
    }
    else {
        document.getElementById("markerpt").style.display = "none";
    }
    document.getElementById("profile_infos").innerHTML = profile_infos;
    document.getElementById("profile_infos").style.display='inline';
    document.getElementById("curpt_infos").innerHTML = curpt_infos;
    document.getElementById("curpt_infos").style.display='inline';
}

function returnInt(element) {
  return parseInt(element,10);
}

function onChartMouseDown(e,o) {
	var ev = e || window.event;
    var posx = ev.clientX - findPosX(document.getElementById("chartimg"));
	if (ev.button==LEFT_BUTTON) {
        selxLeft = posx;
        refreshSelInfos();
    }
	else if (ev.button==RIGHT_BUTTON) {
        selxPt = posx;
        refreshSelInfos();
    }
}

function onChartMouseUp(e,o) {
	var ev = e || window.event;
	if (ev.button==LEFT_BUTTON) {
		var posx = ev.clientX - findPosX(document.getElementById("chartimg"));
        selxRight = posx;
        refreshSelInfos(1);
    }
}

/* Answer from profile computation */
function onComputeProfileAnswer() {
	if (this.readyState == 4) {
		if (this.status == 200) {
            document.getElementById('compprofileloading').style.display='none';
            var res = this.responseText.split("\n");
            eles = res[0].split(',');
            eles = eles.map(returnInt);
            dists = res[1].split(',');
            dists = dists.map(parseFloat);
            pt2px = res[2].split(',');
            pt2px = pt2px.map(returnInt);
            ptinput2px = res[3].split(',');
            ptinput2px = ptinput2px.map(returnInt);
            refreshGraphDetail();
        }
    }
}

/* Send points for profile computation */
function computeProfile(ptlisturl) {
    var client = new XMLHttpRequest();
    client.open('GET','/profile/'+ptlisturl+'/800/200');
    client.send();
    client.onreadystatechange = onComputeProfileAnswer;
    
    document.getElementById('compprofileloading').style.width="32px";
    document.getElementById('compprofileloading').style.height="32px";
    document.getElementById('compprofileloading').src = '/static/images/loading.svg'; 
    document.getElementById('compprofileloading').style.display="inline";
}

/* When user wants to compute profile */
function onComputeProfileClick() {
    computeProfile(buildPtlistUrl(getLatLonList()));
}

/* Recompute point list string */
function getLatLonList() {
    var out = [];
    var i;
    for(i=0;i<points.length;i++) {
        out[i] = points[i].pt;
    }
    return out;
}


var zooms = {15: 4.777302*256, 16: 2.388657*256};
var x0s = {15: -20037508, 16: -20037508};
var y0s = {15: 20037508, 16: 20037508};

function latlon2tilerowcol(lat,lon,matrix) {
    //lat,lon -> Mercator
    var x = 111319.49079327357 * lon; // a*2*pi/360
    var y = 6378137.0 * Math.log(Math.tan((lat*0.0087266462599716) + Math.PI/4));
    return [(x-x0s[matrix]) / zooms[matrix] | 0, (y0s[matrix]-y) / zooms[matrix] | 0];
}

function getTilesBounds(matrix) {
    var i;
    var lat;var lon;
    var minlat,minlon,maxlat,maxlon;
    if(points.length<1) return null;
    minlat = points[0].pt.lat;
    maxlat = points[0].pt.lat;
    minlon = points[0].pt.lon;
    maxlon = points[0].pt.lon;
    for (i=1;i<points.length;i++) {
        lat = points[i].pt.lat;
        lon = points[i].pt.lon;
        if(lat<minlat)minlat = lat;
        if(lat>maxlat)maxlat = lat;
        if(lon<minlon)minlon = lon;
        if(lon>maxlon)maxlon = lon;
    }
    var t1 = latlon2tilerowcol(minlat,minlon,matrix);
    var t2 = latlon2tilerowcol(maxlat,maxlon,matrix);
    return [t1[0],t2[0],t2[1],t1[1]];
}

function getTiles(key,matrix,element) {
    var bounds = getTilesBounds(15);
    var row,col;
    var out=[];
    var img;
    element.style.height = ((bounds[3]-bounds[2]+1)*256)+"px";
    element.style.width = ((bounds[1]-bounds[0]+1)*256)+"px";
    for(row=bounds[2];row<=bounds[3];row++) {
        for(col=bounds[0];col<=bounds[1];col++) {
            var img = document.createElement("img");
            img.src = "http://wxs.ign.fr/"+key+"/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX="+matrix+"&TILEROW="+row+"&TILECOL="+col+"&FORMAT=image%2Fjpeg";
            img.style.left = ((col-bounds[0])*256)+"px";
            img.style.top = ((row-bounds[2])*256)+"px";
            img.style.width='256px';
            img.style.height='256px';
            img.setAttribute("alt",row+","+col);
            element.appendChild(img);
            out.push(img.style.left+"."+img.style.top+","+row+","+col+"\n");
            out.push("http://wxs.ign.fr/"+key+"/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX="+matrix+"&TILEROW="+row+"&TILECOL="+col+"&FORMAT=image%2Fjpeg");
        }
    }
    return out;
}

function onBuildMapClick() {
    var myWindow = window.open("","Printable map","width=200,height=100,menubar=yes");
    var e = myWindow.document.createElement("div");
    myWindow.document.body.appendChild(e);
    tiles = getTiles(GeoPortalApiKey,15,e);
}


function refreshGraph() {
    //console.log("refreshGraph");
    profiledata = [];
    var i;
    for(i=0;i<points.length;i++) {
        profiledata.push([points[i].pt.dist,points[i].pt.ele]);
    }
    $.plot($("#profilechart"), [profiledata], options);
}

function refreshGraphDetail() {
    //console.log("refreshGraphDetail");
    profiledata = [];
    var i;
    for(i=0;i<points.length;i++) {
        profiledata.push([points[i].pt.dist,points[i].pt.ele]);
    }
    profiledatadetail = [];
    var i;
    for(i=0;i<eles.length;i++) {
        profiledatadetail.push([dists[i],eles[i]]);
    }
    $.plot($("#profilechart"), [profiledata,profiledatadetail], options);
}

var options = {
    series: {
        lines: {
            show: true
        },
        points: {
            show: false
        }
    },
    legend: {
        noColumns: 2
    },
    xaxis: {
        tickDecimals: 0
    },
    yaxis: {
        //min: 0
    },
    selection: {
        mode: "x"
    },
    grid:{clickable: true}
};
var profiledata=[];
$(function() {
    $.plot($("#profilechart"), [profiledata], options);
});


function getRiver(name) {
    $.getJSON('/river/'+name, addRiverToMap).fail(function(err){$("#svrresponse").html(err.responseText);});
}

var current_parcours_id;
var current_deb; // debarquement (1) ou embarquement (0)

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

function flush() {
    $.get('/flush',function(){$("#svrresponse").html('OK');}).fail(function(err){$("#svrresponse").html(err.responseText);});
}

function search_river(evt,river_name) {
    if(evt.keyCode==13) {
        getRiver(river_name);
    }
}

var current_river;

function addRiverToMap(river_obj) {
    $("#river_name").html(river_obj['name']);
    river_points = [];
    var i;
    var j;
    //var k = 0;
    var pts=[];
    for(i=0;i<river_obj.paths.length;i++) {
        pts[i]=[];
        for(j=0;j<river_obj.paths[i].length;j++) {
            pts[i][j] = {"lat": river_obj.paths[i][j][0], "lon": river_obj.paths[i][j][1],"name":" "+i+" "+j};
            //k++;
        }
    }
    addRiverPoints(pts);
    current_river = river_obj['name'];
    //console.log(river_obj);
    var i=-1;
    $("#nb_paths").html(river_obj.paths.length);
    if ("parcours" in river_obj) {
      $("#parcours").html('<ul><li>'+river_obj.parcours.map(function(p) { i++; return p.name + '<ul><li onClick="setEmb(this,\''+current_river+'\','+i+');" class="emb_deb">Emb:'+p.embarquement+'</li><li onClick="setDeb(this,\''+current_river+'\','+i+');" class="emb_deb">Deb:'+p.debarquement+'</li></ul>'; }).join('</li><li>')+'</li></ul>');
    } else {
      $("#parcours").html('<b>No parcours in db</b>');
    }
    var i=-1;
    if ("routes_rivermap" in river_obj) {
      $("#rivermap").html('<ul><li>'+river_obj.routes_rivermap.map(function(p) { i++; return ''+i+': ' +p.name + ': ' + p.length + ' km '+p.ww_class }).join('</li><li>')+'</li></ul>');
      for(i=0;i<river_obj.routes_rivermap.length;i++) {
          addPointRivermap(river_obj.routes_rivermap[i].start,'S'+i);
          addPointRivermap(river_obj.routes_rivermap[i].end,'E'+i);
      }
    } else {
      $("#rivermap").html('<b>No routes in db</b>');
    }
}
