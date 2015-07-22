
define(['jquery', 'gmaps'],
function ($, gmaps){

function SegmentView(SegmentGroup, container, viewFunc){

	if (typeof container === 'undefined'){
		container = $('#container');
	}

	if (typeof viewFunc !== 'undefined'){
		viewFunc(SegmentGroup);
		return;
	}
	this.container = container;
	this.SegmentGroup = SegmentGroup;

	this.render();
};

SegmentView.prototype.init_divs_additional = null;

SegmentView.prototype.createInfo = function(){
	try {
		var start_stamp = this.SegmentGroup.segments[0].start.monotonic_timestamp;
		var end_stamp = this.SegmentGroup.segments[this.SegmentGroup.segments.length-1].end.monotonic_timestamp;
		var start_time = new Date(start_stamp*1000);
		var end_time = new Date(end_stamp*1000);

		this.info.append($('<p>').text(String(start_time)));
		this.info.append($('<p>').text(String(end_time)));
	} catch (e){}

}

SegmentView.prototype.init_divs = function(){
	this.parent = $('<div>').addClass('map-container');
	this.map_div = $('<div>').addClass('map-canvas');
	this.info = $('<div>').addClass('map-info');
	this.map = new google.maps.Map(this.map_div[0], {disableDefaultUI: true});
	if (this.init_divs_additional !== null){
		this.init_divs_additional();
	}
};

SegmentView.prototype.render = function(){
	this.init_divs();
	this.SegmentGroup.createLines(this.map);
	this.map.fitBounds(this.SegmentGroup.bounds);
	this.createInfo();
	this.parent.append(this.map_div, this.info);
	this.container.append(this.parent);
}

return SegmentView;

});

