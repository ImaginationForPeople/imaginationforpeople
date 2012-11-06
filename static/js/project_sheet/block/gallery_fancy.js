
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

$(document).ready(function(){
	// local helper to display upper side pictures
	function gallery_fancy_display() {

	}

	// FIXME: change i4p prefix with a local one (gallery-fancy-...)
	// enable slider
	$('*[data-toggle="i4p-gallery-fancy-slider"]').each(function(){
		var sliderThis = this;
		var viewerObjSelector = $(this).attr('data-slider-view');

		var backText = $(sliderThis).attr('data-slider-backtext') || "prev";
		var forwardText = $(sliderThis).attr('data-slider-forwardtext') || "next";

		// initialize the lower side (wide thumb slider with a full list)
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
		console.log('gallery-fancy: initialized bottom slider!');

		console.log("gallery-fancy: data-slider-view = " + viewerObjSelector);
		console.log($(viewerObjSelector));


		// make all slides fully active
		$('*[data-toggle="i4p-gallery-fancy-slider"] a').each(function(){
			var linkThis = this;
			var linkNumber = $(linkThis).parent().attr('data-slide-number');
			var linkSrc= $(linkThis).attr('href');
			// console.log('gallery-fancy: parsing link : '+linkThis);

			// populate upper slider here
			// FIXME: maybe use pure.js ?
			$(viewerObjSelector).append('<li><img src="' + linkSrc + '" /></li>')
				
			// bind click event
			$(linkThis).click(function(event){
				event.preventDefault();
				console.log('FIXME: show slide slide '+linkNumber+' on upper slider');
			});
		});
		console.log('gallery-fancy: initialized slides!');
		console.log($(viewerObjSelector));


		// initialize upper slider (with nothing inside)
		$(viewerObjSelector).anythingslider({
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
			infiniteSlides: true, // no wrap
			changeBy: 1
		});
		console.log('gallery-fancy: initialized top slider!');

		console.log('gallery-fancy: active!');
	});

	// enable slider controllers
	$('*[data-toggle="i4p-gallery-fancy-modal-control"]').each(function(){
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

