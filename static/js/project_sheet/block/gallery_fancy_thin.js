
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

/*jslint browser: true*/
/*global $, jQuery, document*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

"use strict";

$(document).ready(function () {

	var jdebug = function (str) { console.log('gallery-fancy: ' + str); };

	// enable slider controllers first (to be ready in case a slider fails/slows)
	$('*[data-toggle="i4p-gallery-modal-control"]').click(function (e) {
		var targetId = $(this).attr('data-slider-target-id'),
			command = $(this).attr('data-slider-command'),
			targetSlider = $('#' + targetId).data('AnythingSlider');

		if (!targetSlider) { $.error('AnythingtargetSlider not initialized on object ' + targetId); }

		switch (command.toLowerCase()) {
		case 'goforward':
			targetSlider.goForward();
			break;
		case 'goback':
			targetSlider.goBack();
			break;
		default:
			jdebug("send '" + command + "' to object id " + targetId);
		}
		e.preventDefault();
	});

	jdebug('initialized modal controls!');

	// enable lower slider
	$('*[data-toggle="i4p-gallery-fancy-slider"]').each(function () {
		var sliderThis = this,
			sliderViewId = $(this).attr('data-slider-view-id');

		if (!sliderViewId) { $.error('data-slider-view-id not initialized'); }

		jdebug("data-slider-view = " + sliderViewId);

		// initialize the lower side (wide thumb slider with a full list)
		$(sliderThis).anythingSlider({
			autoPlay: false,
			startStopped: true,

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
		jdebug('initialized bottom slider!');

		// make all slides fully active
		$(sliderThis).find('a').each(function () {
			var linkThis = this,
				linkNumber = $(linkThis).parent().attr('data-slide-number'),
				linkSrc = $(linkThis).attr('href');

			// jdebug('gallery-fancy: parsing link : '+linkThis);

			// populate upper slider here
			// $(viewerObjSelector).append('<li><img src="' + linkSrc + '" alt=""/></li>')

			// bind click event
			$(linkThis).click(function (event) {
				event.preventDefault();
				jdebug('FIXME: show slide slide ' + linkNumber + ' on upper slider');
			});
		});
		jdebug('initialized lower slides!');
	}); // lower slider init


	/*
	// initialize upper slider (with nothing inside)
	$('*[data-toggle="i4p-gallery-fancy-viewer"]').each(function(){
	var sliderThis = this;
	var sliderId = $(sliderThis).attr('id');
	var viewerObjSelector = $(this).attr('data-slider-view');

	jdebug("within fancy-viewer id = " + sliderId );
	// jdebug($(sliderThis));

	$(sliderThis).find('a').each(function(){
	var linkThis = this;
	var linkNumber = $(linkThis).parent().attr('data-slide-number');

	// bind click event
	$(linkThis).click(function(event){
	event.preventDefault();
	jdebug('FIXME: show slide slide '+linkNumber+' on lower slider');
	});
	});

	jdebug('initialized upper slides!');
	jdebug($(viewerObjSelector));
	if (!viewerObjSelector){ $.error('no viewerObjSelector defined'); }
	jdebug('that was the viewerObjSelector!');

	$(sliderThis).anythingslider({
	autoPlay: false,
	startStopped: true, 

	buildArrows: false, // no prev/next arrows
	buildNavigation: false, // no tabs
	buildStartStop: false, // no start/stop
	hashTags: false,

	expand: false,
	resizeContents: false,
	});
	});
	jdebug('initialized top slider!');
	*/

	jdebug('init DONE');
});

