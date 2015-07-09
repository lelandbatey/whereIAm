
requirejs.config({
	baseUrl: 'static',
	paths: {
		async: 'requirejs-plugins/async',
		jquery: '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery',
	}
});

define ('gmaps', ['async!https://maps.googleapis.com/maps/api/js?key=AIzaSyB5l8Y_pDgxKIp2K1icKCHcUcoQ0b_SVGU&sensor=true&libraries=geometry'],
	function () {
		return google.maps;
	}
);

require(
	[
		'jquery',
		'GpsCoordGroup',
		'DateParse',
		'gmaps'
	], 
	function ($, GpsCoordGroup, DateParse, gmaps) {
		"use strict";
		function mapCoordinatePairs(inputData) {
			var container = document.getElementById("container");
			var maxMapCount = 200;
			if (maxMapCount > inputData.length-1) { maxMapCount = inputData.length-1; }
			window.MAX_MAP_COUNT = maxMapCount;

			for (var i = 1; i < maxMapCount; i++){
				var group = new GpsCoordGroup(inputData, i);
				// console.log(group);

				var parent = document.createElement("div");
				parent.className = "map-container";
				var elm = document.createElement("div");
				elm.className = "map-canvas";
				var info = document.createElement("pre");
				info.className = "map-info";

				var map = new google.maps.Map(elm, {disableDefaultUI: true});

				group.createLines(map);
				map.fitBounds(group.bounds);

				var infoContent = document.createTextNode(group.debug_info);
				info.appendChild(infoContent);
				parent.appendChild(elm);
				parent.appendChild(info);
				container.appendChild(parent);
			}
		}

		function initialize() {
			console.log("Initialize getting called.");
			var start = "08:30:00 01-06-15";
			var end =   "18:00:00 01-06-15";

			start = new DateParse(start).getTime()/1000;
			end = new DateParse(end).getTime()/1000;

			console.log(start);
			console.log(end);

			$.ajax({
				url: '/data_range/'+start+'.0/'+end+'.0',
				// url: '/last_range/800',
				dataType: 'json',
				success: mapCoordinatePairs
			});
		}
		$(initialize);
	}
);


