
/* Compute distance between two points of the earth geoid (approximated to a sphere)
   Input is in degrees and output in meters */
function geodeticDist(lat1,lon1,lat2,lon2) {
	// convert inputs in degrees to radians
	var lat1 = lat1 * 0.0174532925199433;
	var lon1 = lon1 * 0.0174532925199433;
	var lat2 = lat2 * 0.0174532925199433;
	var lon2 = lon2 * 0.0174532925199433;
	// just draw a schema of two points on a sphere and two radius and you'll understand
	var a = Math.sin((lat2 - lat1)/2)*Math.sin((lat2 - lat1)/2) + Math.cos(lat1) * Math.cos(lat2) * Math.sin((lon2 - lon1)/2)*Math.sin((lon2 - lon1)/2);
	var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
	// earth mean radius is 6371 km
	return (6371000.0 * c);
}

/* Compute course from (lat1,lon1) to (lat2,lon2)
   Input is in degrees and output in degrees */
function computeCourse(lat1,lon1,lat2,lon2) {
  //convert inputs in degrees to radians
  lat1 = lat1 * 0.0174532925199433;
  lon1 = lon1 * 0.0174532925199433;
  lat2 = lat2 * 0.0174532925199433;
  lon2 = lon2 * 0.0174532925199433;
  var y = Math.sin(lon2 - lon1) * Math.cos(lat2);
	var x = Math.cos(lat1)*Math.sin(lat2) - Math.sin(lat1)*Math.cos(lat2)*Math.cos(lon2 - lon1);
	return (((Math.atan2(y, x) * 180 / Math.PI)+360) % 360);
}

/* Compute an angle given 3 points */
function computeAngle(lat1,lon1,lat2,lon2,lat3,lon3) {
    var a1 = computeCourse(lat1,lon1,lat2,lon2);
    var a2 = computeCourse(lat2,lon2,lat3,lon3);
    var r = ((a1-180-a2+360) % 360);
    if (r > 180) {
        r = 360-r;
    }
    return (r);
}
