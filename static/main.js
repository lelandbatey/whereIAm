
requirejs.config({
	baseUrl: 'static',
	paths: {
		tinycolor: 'lib/tinycolor',
		async: 'lib/async',
		jquery: '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery',
	}
});

define ('gmaps', ['async!https://maps.googleapis.com/maps/api/js?key=AIzaSyB5l8Y_pDgxKIp2K1icKCHcUcoQ0b_SVGU&sensor=true&libraries=geometry'],
	function () {
		return google.maps;
	}
);

define ('brain', ['async!lib/brain-0.6.3.js'],
	function () {
		return window.brain;
	}
);

require(
	[
		'jquery',
		'DateParse',
		'gmaps',
		'SegmentSeriesModel',
		'Views'
	],
function ($, DateParse, gmaps, SegmentSeriesModel, Views) {
	"use strict";


	$(document).keypress(function (evnt){
		var container = $('#container');
		// if 'z' key was pressed
		if (evnt.charCode === 122){
			var buttons = container.find('button:enabled');
			var yes_btn = $(buttons[0]);
			yes_btn.trigger('click');

		// if 'x' key was pressed
		} else if (evnt.charCode === 120){
			var buttons = container.find('button:enabled');
			var no_btn = $(buttons[1]);
			no_btn.trigger('click');
		} else if (evnt.charCode === 13){
			console.log(JSON.stringify(window.TRAINING_DATA, null, 4));
		}
	});


	function mapCoordinatePairs(rawData) {
		var container = document.getElementById("container");
		var maxMapCount = 100;
		if (maxMapCount > rawData.length-1) { maxMapCount = rawData.length-1; }
		window.MAX_MAP_COUNT = maxMapCount;
		function makeMap(brain_json){
			for (var i = 0; i < maxMapCount; i++){
			var group = new SegmentSeriesModel(rawData, i);
			console.log(i);

			var view = new Views.SegmentBrainView(group, brain_json);

			}
		}
		$.ajax({
			url: '/static/trained_brain.json',
			dataType: 'json',
			success: makeMap
		});
	}

	function createTrainingGround(rawData){
		var container = $('#container');
		var maxMapCount = 200;
		if (maxMapCount > rawData.length-1) { maxMapCount = rawData.length-1; }
		window.MAX_MAP_COUNT = maxMapCount;

		var groups = [], i;
		var trainingData = [];
		window.TRAINING_DATA = trainingData;

		var click_func_factory = function (index, ybtn, nbtn, info_box, which){
			if (which === 'yes'){
				return function(){
					trainingData.push(groups[index].getTrainingData(true));
					info_box.css('background-color', '#22b43b');
					ybtn.attr('disabled', true);
					nbtn.attr('disabled', true);
					console.log(window.TRAINING_DATA);
				};
			} else if (which === 'no'){
				return function(){
					trainingData.push(groups[index].getTrainingData(false));
					info_box.css('background-color', 'FireBrick');
					ybtn.attr('disabled', true);
					nbtn.attr('disabled', true);
					console.log(window.TRAINING_DATA);
				};
			}
		};

		for (i = 0; i < maxMapCount; i++){
			var group = new SegmentSeriesModel(rawData, i);
			groups.push(group);
			var parent = $('<div>').addClass('map-container');
			var map_div = $('<div>').addClass('map-canvas');
			var info = $('<div>').addClass('map-info');
			var yes_btn = $('<button>').text('Yes');
			var no_btn = $('<button>').text('No');

			yes_btn.click(click_func_factory(i, yes_btn, no_btn, info, 'yes'));
			no_btn.click(click_func_factory(i, yes_btn, no_btn, info, 'no'));

			var map = new google.maps.Map(map_div[0], {disableDefaultUI: true});

			group.createLines(map);
			map.fitBounds(group.bounds);

			try {
				info.append(yes_btn, no_btn);
				info.append($('<p>').text(String(new Date(group.segments[0].start.monotonic_timestamp*1000))));
			} catch (err){
				break;
			}
			parent.append(map_div, info);
			container.append(parent);
		}
	}

	function wideTimeSpread(rawData, callback){
		var container = $('#container');
		var maxMapCount = 100;
		if (maxMapCount > rawData.length-1) { maxMapCount = rawData.length-1; }
		window.MAX_MAP_COUNT = maxMapCount;

		var groups = [], i;
		for (i = 0; groups.length < maxMapCount; i+=20){
			var group = new SegmentSeriesModel(rawData, i, 20);
			groups.push(group);
			var parent = $('<div>').addClass('map-container');
			var map_div = $('<div>').addClass('map-canvas');
			var info = $('<div>').addClass('map-info');

			var map = new google.maps.Map(map_div[0], {disableDefaultUI: true});

			group.createLines(map);
			map.fitBounds(group.bounds);
			gmaps.event.addListenerOnce(map, 'idle', function() {
				gmaps.event.trigger(map, 'resize');
			});

			try {
				info.append($('<p>').text(String(new Date(group.segments[0].start.monotonic_timestamp*1000))));
				info.append($('<p>').text(String(new Date(group.segments[group.segments.length-1].end.monotonic_timestamp*1000))));
			} catch (e){
				break;
			}
			parent.append(map_div, info);
			container.append(parent);
		}
		// window.setTimeout(callback, 10000);
		// console.log(callback);
		// callback();
	}


	function initialize() {
		console.log("Initialize getting called.");
		var start = "11:45:00 20-06-15";
		var end =   "13:00:00 20-06-15";

		start = new DateParse(start).getTime()/1000;
		end = new DateParse(end).getTime()/1000;

		console.log(start);
		console.log(end);
		console.log('Length of time:', (end-start)/60)

		$.ajax({
			url: '/data_range/'+start+'.0/'+end+'.0',
			dataType: 'json',
			success: mapCoordinatePairs
			// success: wideTimeSpread
		});
	}

	function viewJuneDay(day, callback){
		console.log("Initialize getting called.");
		var start = "06:00:00 "+day+"-06-15";
		var end =   "20:00:00 "+day+"-06-15";

		start = new DateParse(start).getTime()/1000;
		end = new DateParse(end).getTime()/1000;

		console.log(start);
		console.log(end);

		$.ajax({
			url: '/data_range/'+start+'.0/'+end+'.0',
			dataType: 'json',
			// success: createTrainingGround
			success: function(data){
				window.setTimeout(function(){
					wideTimeSpread(data, callback);
				}, 1000);
			}
		});
	}

	$(initialize);
	// $(viewJuneDay(20));
	// $(function(){
	// 	var number_of_days = 3;
	// 	var startday = 1;
	// 	var i = 0;
	// 	function newDay(){
	// 		console.log("calling newDay");
	// 		$('#container').removeAttr('id');
	// 		$('body').append($('<div>').attr('id', 'container'));
	// 		if (i < number_of_days) {
	// 			i++;
	// 			window.setTimeout(function (){
	// 				viewJuneDay(startday+i, newDay);
	// 			}, 5000);
	// 		}
	// 	};

	// 	viewJuneDay(startday+i, newDay);
	// });
}
);


