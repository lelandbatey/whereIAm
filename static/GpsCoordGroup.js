define("GpsCoordGroup", ['./tinycolor.js'], function (tinycolor){
	return function (rawData, index, count, maxMapCount) {
		// maxMapCount is optional, and will load from global
		// `window.MAX_MAP_COUNT` if it exists, otherwise it defaults to 100
		if (arguments.length < 4) {
			if (typeof window.MAX_MAP_COUNT === 'undefined') {
				maxMapCount = 100;
			} else {
				maxMapCount = window.MAX_MAP_COUNT;
			};
		};

		// The optional `count` defaults to 100
		if (arguments.length < 2) {
			count = 4;
		};

		this.debug_info = "";
		this.debugInfo = function(to_log){this.debug_info += String(to_log);}
		this.coords = [];
		this.indices = [];

		// [i-1] -- [ i ] -- [i+1] -- [i+2]
		for (var i = -1; i < count; i++){
			if (index+i < len) {
				var latlng = rawToLatLng(rawData[index+i]);
				this.indices.push(index+i);
				this.coords.push(latlng);
			};
		}

		
	}
});