
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

$(document).ready(function(){
	// enable slider
	$('*[data-toggle="i4p-slider"]').each(function(){
		var sliderThis = this;
		var viewerObjSelector = $(this).attr('data-slider-view');
		console.log("new viewerObjSelector: "+viewerObjSelector);

		var backText = $(sliderThis).attr('data-slider-backtext') || "prev";
		var forwardText = $(sliderThis).attr('data-slider-forwardtext') || "next";

		$(sliderThis).anythingSlider({
			autoPlay: false,
			startStopped: true, 
			forwardText: forwardText,
			backText: backText,

			buildArrows: false, // no prev/next arrows
			buildNavigation: false, // no tabs
			buildStartStop: false, // no start/stop
			hashTags: false,

			expand: false,
			resizeContents: false,
			showMultiple: 5,
			infiniteSlides: true, // no wrap
			changeBy: 5
		});
	});

	// enable slider controllers
	$('*[data-toggle="i4p-slider-control"]').each(function(){
		var controlThis = this;

		$(controlThis).click(function(e){
			var target = '#' + $(controlThis).attr('data-slider-target');
			var command = $(controlThis).attr('data-slider-command');
			switch (command.toLowerCase()) {
			case 'goforward':
				$(target).data('AnythingSlider').goForward();
				break;
			case 'goback':
				$(target).data('AnythingSlider').goBack();
				break;
			default:
				console.log("send '" + command + "' to " + target);
			}
			e.preventDefault();
		});
	});

});

