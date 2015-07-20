
define('trainingGroundView', ['jquery', 'SegmentView'],
function ($, SegmentView){

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
return function(SegmentGroup, container){
	if (typeof container === 'undefined'){
		container = $('#container');
	}

	this.init_divs_additional = function(){
		this.yes_btn = $('<button>').text('Yes');
		this.no_btn = $('<button>').text('No');
	};
	this.init_divs = SegmentView.prototype.init_divs;
	this.render = SegmentView.prototype.render;
}

});

