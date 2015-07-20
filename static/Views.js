
define('Views', ['SegmentView', 'SegmentBrainView'],
function (SegmentView, SegmentBrainView){
	return {
		vanilla: SegmentView,
		BrainView: SegmentBrainView,
		Standard: SegmentView,
		SegmentView: SegmentView,
		SegmentBrainView: SegmentBrainView
	}
});
