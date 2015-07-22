
define(['jquery', 'gmaps', 'lib/brain-0.6.3', 'views/SegmentView'],
function ($, gmaps, brain, SegmentView){

function SegmentBrainView(SegmentGroup, brain_json, container){

	if (typeof container === 'undefined'){
		container = $('#container');
	}
	this.brain_json = brain_json;
	this.container = container;
	this.SegmentGroup = SegmentGroup;

	this.render();
};

SegmentBrainView.prototype = Object.create(SegmentView.prototype);

SegmentBrainView.prototype.classify_with_net = function (){
	this.net = new window.brain.NeuralNetwork();
	this.net.fromJSON(this.brain_json);
	var brain_data = this.SegmentGroup.getTrainingData();
	this.net_output = this.net.run(brain_data.train_data);
}

SegmentBrainView.prototype.createInfo = function (){
	this.classify_with_net();
	var text = $('<pre>');
	var move = 'moving: '+this.net_output.moving.toFixed(3)+"\n";
	var stop = 'motionless: '+this.net_output.motionless.toFixed(3)+"\n";
	text.text(move+stop);
	this.info.append(text);
	if (this.net_output.motionless > this.net_output.moving){
		this.info.css('background-color', 'FireBrick');
	} else {
		this.info.css('background-color', '#22b43b');
	}
}

SegmentBrainView.prototype.constructor = SegmentBrainView;

return SegmentBrainView;

});
