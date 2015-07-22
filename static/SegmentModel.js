
define('SegmentModel', ['gmaps'], function(gmaps){

function rawToLatLng(inval){
	return new gmaps.LatLng(inval.latitude, inval.longitude);
}

function SegmentModel(raw_data, index){
	function modifyPoint(index){
		var obj = raw_data[index];
		obj.index = obj.index || index;
		obj.gmapObj = rawToLatLng(obj);
		return obj;
	}
	this.start = modifyPoint(index-1);
	this.end = modifyPoint(index);

	// This length is in meters
	this.linear_length = gmaps.geometry.spherical.computeDistanceBetween(this.start.gmapObj, this.end.gmapObj);
	// this.bearing = normalizeRadian(this.end.derived_bearing);
	this.bearing = this.end.derived_bearing;
	this.bearing_difference = null;

	var time_dist = this.end.monotonic_timestamp - this.start.monotonic_timestamp;
	// Speed is in meters/second
	this.speed = this.linear_length/time_dist;
};

return SegmentModel;
});

