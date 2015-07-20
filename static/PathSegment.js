define("PathSegment", ['tinycolor', 'gmaps'], function (tinycolor, gmaps){

/**
 * @brief Definition of PathSegment object, representing a group of paths
 * @details A PathSegment object represents a group of `Segment` objects, with convenience methods for working with those segments. For example, mapping those segments on a Google Map.
 *
 * @param rawData a list of objects, typically originating as the response from the server to a request for data over a time range.
 * @param index The index of the first entry in rawData from which to create the series of Segment objects
 * @param count The maximum number of segments that should represented by this `PathSegment`
 * @return A PathSegment object which represents a maximum of `count` objects. The number of `Segment` objects may not be equal to `count` if there aren't enough entries in rawData after position `index` to derive the number of segments specified by `count`.
 */

return function (rawData, index, count) {
	'use strict';

	// The optional `count` defaults to 4
	if (arguments.length < 3) {
		count = 4;
	}

	/*
		Takes an object with `latitude` and `longitude` attributes and converts
		them to a GoogleMaps LatLng object.
	*/
	function rawToLatLng(inval){
		return new gmaps.LatLng(inval.latitude, inval.longitude);
	}
	function normalizeRadian(r){
		r = r % (Math.PI*2.0);
		r = (r + (Math.PI*2.0)) % (Math.PI*2.0);
		return r;
	}
	function translate_domain(d_start, d_stop, d_val, n_start, n_stop){
		var d = d_stop - d_start;
		var v = d_val - d_start;
		var ratio = v/d;
		var nd = n_stop - n_start;
		var nv = (ratio * nd) + n_start;
		return nv;
	}
	function bearingToColor(bearing){
		var linehue = Math.round((180/Math.PI)*bearing);
		if (linehue < 0) { linehue += 360; }
		return tinycolor("hsl("+String(linehue)+", 100%, 50%)").toHexString();
	}

	function Segment (_index) {
		function modifyPoint(_index){
			var obj = rawData[_index];
			obj.index = _index;
			obj.gmapObj = rawToLatLng(obj);
			return obj;
		}
		this.start = modifyPoint(_index-1);
		this.end = modifyPoint(_index);

		// This length is in meters
		this.linear_length = gmaps.geometry.spherical.computeDistanceBetween(this.start.gmapObj, this.end.gmapObj);
		// this.bearing = normalizeRadian(this.end.derived_bearing);
		this.bearing = this.end.derived_bearing;
		this.bearing_difference = null;

		var time_dist = this.end.monotonic_timestamp - this.start.monotonic_timestamp;
		// Speed is in meters/second
		this.speed = this.linear_length/time_dist;
	}

	var i;

	this.segments = [];
	// for (i = 0; i < count; i++){
	for (i = 1; this.segments.length < count; i++){
		if ((index+i) < rawData.length-1) {
			this.segments.push(new Segment(index+i));
		} else {
			break;
		}
		// if (i > 50000){ throw "Got into an infinite loop"};
	}

	for (i = 1; i < this.segments.length; i++){
		var cur_seg = this.segments[i];
		var pas_seg = this.segments[i-1];

		// function mod(a, n){
		// 	return (a % n + n) % n;
		// }


		var bd = cur_seg.bearing - pas_seg.bearing;
		cur_seg.bearing_difference = bd;
		if (bd > Math.PI) {
			cur_seg.bearing_difference = bd - (2*Math.PI);
		} else if (bd < -Math.PI){
			cur_seg.bearing_difference = bd + (2*Math.PI);
		}
	}

	this.bounds = new gmaps.LatLngBounds();
	for (i = 0; i < this.segments.length; i++){
		var seg = this.segments[i];
		this.bounds.extend(seg.start.gmapObj);
		this.bounds.extend(seg.end.gmapObj);
	}

	this.createLines = function (map, color_style){
		if (arguments.length < 2) {
			color_style = 'difference';
		}
		for (i = 0; i < this.segments.length; i++){
			var line_color;
			if (color_style === 'difference') {
				line_color = tinycolor('grey');
				var bearing_diff = this.segments[i].bearing_difference;
				if (bearing_diff !== null) {
					line_color = bearingToColor(bearing_diff+Math.PI);
				}
			} else {
				var bearing = this.segments[i].derived_bearing;
				line_color = bearingToColor(bearing);
			}
			var line_symbol = {
				scale: 2,
				path: gmaps.SymbolPath.FORWARD_OPEN_ARROW
			};
			new gmaps.Polyline({
				path: [this.segments[i].start.gmapObj, this.segments[i].end.gmapObj],
				geodesic: true,
				strokeColor: line_color,
				strokeOpacity: 1.0,
				strokeWeight: 4,
				map: map,
				icons: [{
					icon: line_symbol,
					offset: '100%'
				}]
			});
		}
	};

	this.getTrainingData = function (is_moving){
		var rv = {};
		var train_data = {};
		for (i = 1; i < this.segments.length; i++){
			// Since the neural net I'm using requires that training data be a
			// float between 0 and 1, I have to map a speed and angle
			// difference to a float. I've set the max-speed limit of 500 m/s
			// which is about 1200 Miles/hour, which is twice as fast as the
			// fastest commercial jet in the world, which I figure is the
			// fastest I will likely ever travel.
			var max_speed = 500, min_speed = 0;
			var raw_speed = this.segments[i].speed;
			raw_speed = raw_speed > 0.4 ? raw_speed : 0.0;
			var speed = Math.min(max_speed, Math.max(raw_speed, min_speed));
			speed = translate_domain(min_speed, max_speed, speed, 0, 1);

			var bearing_diff = this.segments[i].bearing_difference;
			bearing_diff = translate_domain(-Math.PI, Math.PI, bearing_diff, 0, 1);
			if (bearing_diff < 0.0 || bearing_diff > 1.0) {
				console.log('raw_bearing_diff:', this.segments[i].bearing_difference);
				console.log("Bearing_diff:", bearing_diff);
				throw "Error: bearing_diff is not within bounds of valid training data.";
			}

			train_data[i+'bearing_diff'] = bearing_diff;
			train_data[i+'speed'] = speed;
		}
		rv.train_data = train_data;
		rv.segments = this.segments;
		var first = this.segments[0].start.index;
		var last = this.segments[this.segments.length-1].end.index;
		rv.first_index = first;
		rv.last_index = last;

		if (typeof is_moving !== 'undefined') {
			rv.is_moving_human_evaluation = is_moving
		}

		return rv;
	};
	this.debug_info = "";
	for (var i = 0; i < this.segments.length; i++) {
		this.debug_info += "diff"+i+': '+this.segments[i].bearing_difference+'\n';
	};
	// console.log(this.debug_info);
	// console.log(this.segments);
	// console.log('\n');
};
});
