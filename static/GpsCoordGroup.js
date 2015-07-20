define("GpsCoordGroup",
	['tinycolor', 'gmaps'],
	function (tinycolor, gmaps){
	return function (rawData, index, count, maxMapCount) {
		"use strict";
		// maxMapCount is optional, and will load from global
		// `window.MAX_MAP_COUNT` if it exists, otherwise it defaults to 100
		if (arguments.length < 4) {
			if (typeof window.MAX_MAP_COUNT === 'undefined') {
				maxMapCount = 100;
			} else {
				maxMapCount = window.MAX_MAP_COUNT;
			}
		}

		// The optional `count` defaults to 4
		if (arguments.length < 3) {
			count = 4;
		}

		this.debug_info = "";
		this.debug = function(to_log){this.debug_info += String(to_log);};
		this.coords = [];
		this.indices = [];
		
		/*
			Takes an object with `latitude` and `longitude` attributes and converts
			them to a GoogleMaps LatLng object.
		*/
		this.rawToLatLng = function (inval){
			return new gmaps.LatLng(inval.latitude, inval.longitude);
		};

		this.bearingToColor = function (bearing){
			var linehue = Math.round((180/Math.PI)*bearing);
			if (linehue < 0) { linehue += 360; }
			return tinycolor("hsl("+String(linehue)+", 100%, 50%)").toHexString();
		};

		this.normalizeRadian = function (r){
			r = r % (Math.PI*2.0);
			r = (r + (Math.PI*2.0)) % (Math.PI*2.0);
			return r;
		};

		var i;
		// [i-1] -- [ i ] -- [i+1] -- [i+2]
		for (i = -1; i < count; i++){
			if (index+i < maxMapCount) {
				var latlng = this.rawToLatLng(rawData[index+i]);
				this.indices.push(index+i);
				this.coords.push(latlng);
				console.log(rawData[index+i]);
			}
		}

		this.bounds = new gmaps.LatLngBounds();
		for (i = 0; i < this.coords.length-1; i++){
			this.bounds.extend(this.coords[i]);
		}

		this.createLines = function (map) {
			for (var i = 1; i < this.coords.length-1; i++){
				var bearing = rawData[this.indices[i]].derived_bearing;
				bearing = this.normalizeRadian(bearing);
				var lineColor = this.bearingToColor(bearing);

				if (i > 1) {
					var prevBearing = rawData[this.indices[i-1]].derived_bearing;
					prevBearing = this.normalizeRadian(prevBearing);
					var diff = Math.abs(bearing - prevBearing) % Math.PI;
					this.debug("prevBearing: "+prevBearing+"\n");
					this.debug("currBearing: "+bearing+"\n");
					this.debug("diff: "+diff+"\n");
					lineColor = this.bearingToColor(Math.PI+diff);
				}

				var lineSymbol = {
					scale: 2,
					path: gmaps.SymbolPath.FORWARD_OPEN_ARROW
				};
				new gmaps.Polyline({
					path: [this.coords[i-1], this.coords[i]],
					geodesic: true,
					strokeColor: lineColor,
					strokeOpacity: 1.0,
					strokeWeight: 4,
					map: map,
					icons: [{
						icon: lineSymbol,
						offset: '100%'
					}]
				});
			}
		};
	};
});
