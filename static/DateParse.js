define('DateParse', function (){
	return function (dateStr){
		// Assumes the date is formatted as such: "%H:%M:%S %d-%m-%y"
		var left = dateStr.split(' ')[0];
		var right = dateStr.split(' ')[1];

		left = left.split(':');
		right = right.split('-');
		var hour   = +left[0];
		var minute = +left[1];
		var second = +left[2];

		var day   = +right[0];
		var month = +right[1]-1;
		var year  = +right[2]+2000;
		// console.log(year, month, day, hour, minute, second, 0);
		var outDate = new Date(year, month, day, hour, minute, second, 0);
		return outDate;
	}
});