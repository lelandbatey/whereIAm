
define("SegmentSeriesModel", ['tinycolor', 'gmaps', 'SegmentModel'], function (tinycolor, gmaps, SegmentModel){
console.log(SegmentModel);
/**
 * @brief Definition of SegmentSeriesModel object, a model for a series of Segment objects
 * @details A PathSegment object represents a group of `Segment` objects, with convenience methods for working with those segments. For example, mapping those segments on a Google Map.
 *
 * @param rawData a list of objects, typically originating as the response from the server to a request for data over a time range.
 * @param index The index of the first entry in rawData from which to create the series of Segment objects
 * @param count The maximum number of segments that should represented by this `PathSegment`
 * @return A PathSegment object which represents a maximum of `count` objects. The number of `Segment` objects may not be equal to `count` if there aren't enough entries in rawData after position `index` to derive the number of segments specified by `count`.
 */
function SegmentSeriesModel(raw_data, index, count){
	'use strict';
	// The optional `count` defaults to 4
	if (arguments.length < 3) {
		count = 4;
	}

	this.raw_data = raw_data;
	this.index = index;
	this.count = count;
	this.segments = [];
	this.bounds = new gmaps.LatLngBounds();

	var i;

	if (typeof this.raw_data.segments !== 'undefined'){
		this.initSegmentsFromTraining();
	} else {
		this.initSegments();
	}


	// Set the proper bearing differences for the various `SegmentModel`s
	for (i = 1; i < this.segments.length; i++){
		var cur_seg = this.segments[i];
		var pas_seg = this.segments[i-1];
		var bd = this.bearing_difference(pas_seg.bearing, cur_seg.bearing);
		cur_seg.bearing_difference = bd;
	}


	// Set the proper bounds for this group
	for (i = 0; i < this.segments.length; i++){
		var seg = this.segments[i];
		this.bounds.extend(seg.start.gmapObj);
		this.bounds.extend(seg.end.gmapObj);
	}
};

SegmentSeriesModel.prototype.initSegments = function (){
	// Since the "SegmentModel" object looks at in index one-prior to the index
	// passed to it, we must anticipate this and start at 1
	for (i = 1; this.segments.length < this.count; i++){
		if ((this.index+i) < this.raw_data.length-1) {
			this.segments.push(new SegmentModel(this.raw_data, this.index+i));
		} else {
			break;
		}
	}
}

SegmentSeriesModel.prototype.initSegmentsFromTraining = function(){
	this.is_moving_human_evaluation = this.raw_data.is_moving_human_evaluation;
	var tsegs = this.raw_data.segments;
	var i = 0;
	// Create segments from segments given in training data
	for (i = 0; i < tsegs.length; i++){
		var temp_array = [];
		temp_array.push(tsegs[i].start);
		temp_array.push(tsegs[i].end);
		this.segments.push(new SegmentModel(temp_array, 1));
	}
}



SegmentSeriesModel.prototype.getTrainingData = function(is_moving){
	var rv = {};
	var train_data = {};
	var i;

	for (i = 1; i < this.segments.length; i++){
		// Since the neural net I'm using requires that training data be a float
		// between 0 and 1, I have to map a speed and angle difference to a
		// float. Since the real concern in regards to speed is more of whether
		// one is moving vs exactly how fast, I've set the max speed to about 20
		// m/s, which is about 40 mph. If the speed is above that, it registers
		// as traveling at the max speed. Additionally, I elected to use a
		// logarithmic scale so that differences at low speeds are more
		// noticable than differences at high speeds.

		var max_speed = 20, min_speed = 0;
		var raw_speed = this.segments[i].speed;
		var speed = 0;
		if (raw_speed < 0.4){
			// 0.4 meters per second is a little bit slower than 1 mph. We if
			// anything is below that, we'll think of it as "not moving" and set
			// `speed` to zero
			speed = 0;
		} else if (raw_speed >= 0.4){
			speed = raw_speed;
			// Some humans do walk at about 0.4 meters per second, though this
			// would be a *very* leisurely mosey. But since 0.4 on the log scale
			// is a negative number, round everything between 1.0 and 0.4 up to
			// 1.01 (1 would be 0 after Math.log) so the neural network can make
			// sense of it.
			if (raw_speed < 1.01){
				speed = 1.01;
			}
			speed = Math.min(max_speed, Math.max(speed, min_speed));
			speed = this.translate_domain(
				min_speed, Math.log(max_speed),
				Math.log(speed),
				0, 1
			);
		}

		var bearing_diff = this.segments[i].bearing_difference;
		// Use the absolute value of the bearing difference. Since the NN
		// expects data to be from 0 to 1, with either representing some
		// extreme, mapping from -pi to +pi would cause most values to hover at
		// about 0.5, which doesn't gell well with the NN.
		bearing_diff = this.translate_domain(0, Math.PI, Math.abs(bearing_diff), 0, 1);
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
		rv.is_moving_human_evaluation = is_moving;
	} else if (typeof this.is_moving_human_evaluation !== 'undefined'){
		rv.is_moving_human_evaluation = this.is_moving_human_evaluation;
	}

	return rv;

}

SegmentSeriesModel.prototype.createLines = function (map, color_style){
	if (arguments.length < 2) {
		color_style = 'difference';
	}
	var i;

	for (i = 0; i < this.segments.length; i++){
		var line_color;
		if (color_style === 'difference') {
			line_color = tinycolor('grey');
			var bearing_diff = this.segments[i].bearing_difference;
			if (bearing_diff !== null) {
				line_color = this.bearingToColor(bearing_diff+Math.PI);
			}
		} else {
			var bearing = this.segments[i].derived_bearing;
			line_color = this.bearingToColor(bearing);
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

}

SegmentSeriesModel.prototype.bearing_difference = function (prior, current){
	var bd = current - prior;
	var rv = bd;
	if (bd > Math.PI) {
		rv = bd - (2*Math.PI);
	} else if (bd < -Math.PI){
		rv = bd + (2*Math.PI);
	}
	return rv;
}

SegmentSeriesModel.prototype.rawToLatLong = function(inval){
	return new gmaps.LatLng(inval.latitude, inval.longitude);
}
SegmentSeriesModel.prototype.normalizeRadian = function (r){
	r = r % (Math.PI*2.0);
	r = (r + (Math.PI*2.0)) % (Math.PI*2.0);
	return r;
}

SegmentSeriesModel.prototype.translate_domain = function (d_start, d_stop, d_val, n_start, n_stop){
	var d = d_stop - d_start;
	var v = d_val - d_start;
	var ratio = v/d;
	var nd = n_stop - n_start;
	var nv = (ratio * nd) + n_start;
	return nv;
}

SegmentSeriesModel.prototype.bearingToColor = function (bearing){
	var linehue = Math.round((180/Math.PI)*bearing);
	if (linehue < 0) { linehue += 360; }
	return tinycolor("hsl("+String(linehue)+", 100%, 50%)").toHexString();
}

return SegmentSeriesModel;
});
