
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

		if (!targetSlider) { console.error('AnythingSlider not initialized on object ' + targetId); }

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
		var lowerSlider = this,
			viewId = $(this).attr('data-slider-view-id');

		// initialize the lower side (wide thumb slider with a 5-set list)
		$(lowerSlider).anythingSlider({
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
		jdebug('initialized bottom slider !');

		// each slides should show upper slider's slide
		$(lowerSlider).find('a').each(function () {
			var linkThis = this,
				linkNumber = $(linkThis).parent().attr('data-slider-index'),
				linkSrc = $(linkThis).attr('href');

			if (linkNumber === undefined) { console.error('data-slider-index not defined'); }

			// bind click event, warning: viewSlider is available at runtime (clicktime) only
			$(linkThis).click(function (event) {
				var viewSlider = $('#' + viewId);
				if (viewSlider === undefined) { console.error('no object for data-slider-view-id = ' + viewId); }

				event.preventDefault();
				jdebug('FIXME: show slide slide ' + linkNumber + ' on upper slider');
				viewSlider.anythingSlider(linkNumber);
			});
		});

		jdebug('initialized lower slides clicks !');
	}); // lower slider init


	jdebug('before fancy viewer');
	// initialize upper slider
	$('*[data-toggle="i4p-gallery-modal-viewer"]').each(function () {
		var upperSlider = this,
			sliderId = $(upperSlider).attr('id');
			// viewId = $(upperSlider).attr('data-slider-view-id');

			console.debug(upperSlider);

		// jdebug(viewId);
		// if (viewId === undefined) {console.error('data-slider-view-id not initialized'); }

/*
			viewSlider = $('#' + viewId).data('AnythingSlider');
		if (!viewSlider) { console.error('AnythingSlider not initialized on object ' + viewId); }
*/

		jdebug('passed fancy viewer init');

		// set links from lower to upper slider
		/*
		$(sliderThis).find('a').each(function () {
			var linkThis = this,
				linkNumber = $(linkThis).parent().attr('data-slide-number');

			// bind click event
			$(linkThis).click(function (event) {
				event.preventDefault();
				jdebug('FIXME: show slide slide ' + linkNumber + ' on lower slider');
			});
		}); */

		// initialize the upper side (large single view)
		$(upperSlider).anythingSlider({
			autoPlay: false,
			startStopped: true,

			buildArrows: false, // no prev/next arrows
			buildNavigation: false, // no tabs
			buildStartStop: false, // no start/stop
			hashTags: false,

			expand: false,
			resizeContents: false
		});
		jdebug('initialized top slider!');
	});

	jdebug('init DONE');
});

