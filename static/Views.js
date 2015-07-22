
define('Views', ['views/SegmentView', 'views/SegmentBrainView'],
function (SegmentView, SegmentBrainView){
	return {
		vanilla: SegmentView,
		BrainView: SegmentBrainView,
		Standard: SegmentView,
		SegmentView: SegmentView,
		SegmentBrainView: SegmentBrainView
	}
});
