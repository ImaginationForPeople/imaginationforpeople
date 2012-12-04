
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

/*jslint browser: true*/
/*global $, jQuery, document*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

"use strict";

$(document).ready(function () {
	var jdebug = function (str) { console.log('memberlist_fancy_square: ' + str); };
	//var jdebug = function (str) { return null; };

	// enable lower slider
	$('*[data-toggle="i4p-memberlist-fancy-slider"]').each(function () {
		var lowerSlider = this,
			viewId = $(this).attr('data-slider-view-id');

		// initialize the lower side (wide thumb slider with a 5-set list)
		$(lowerSlider).anythingSlider({
			autoPlay: false,
			startStopped: true,

			buildArrows: true, // no prev/next arrows
			buildNavigation: true, // no tabs
			buildStartStop: false, // no start/stop
			hashTags: false,

			backText: "&lt;",
			forwardText: "&gt;",

			expand: false,
			resizeContents: false,
			showMultiple: 4,
			infiniteSlides: true, // no wrap
			changeBy: 4
		});
		jdebug('initialized bottom slider !');

	}); // lower slider init

});
