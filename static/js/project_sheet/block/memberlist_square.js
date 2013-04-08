
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

/*jslint browser: true*/
/*global $, jQuery, document, console*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

"use strict";

$(document).ready(function () {
	// var jdebug = function (str) { console.log('memberlist_square: ' + str); };
	var jdebug = function (str) { return null; };

	//
	// Set up the overlay
	//
	// FIXME: document parameters & such
	//
	$('*[data-toggle="i4p-memberlist-overlay"]').each(function () {
		var memberSlider = this,
			viewId = $(this).attr('data-overlay-view-id'),
			viewObj;

		if (viewId === undefined) { console.error('data-overlay-view-id not defined'); }
		viewObj = $('#' + viewId);

		// enable 
		viewObj.hover(function () {
			// display the view
			viewObj.addClass('open-overlay');
		}, function () { // handlerOut
			viewObj.removeClass('open-overlay');
		});

		// enable the view on hover	
		$(memberSlider).find('*[data-toggle="i4p-member-overlay-hook"]')
			.hover(function () { // handlerIn
				var memberHookObj = $(this),
					hookOffset,
					memberImg,
					memberName,
					memberPosition,
					memberContact,
					memberProfile,
					parentOffset;

				// FIXME: fill the view with data
				memberImg = memberHookObj.find('.avatar').attr('src');
				memberName = memberHookObj.attr('data-member-fullname');
				memberPosition = memberHookObj.attr('data-member-position');
				memberContact = memberHookObj.attr('data-member-contact');
				memberProfile = memberHookObj.attr('data-member-profile');

				viewObj.find('.avatar').attr('src', memberImg);
				viewObj.find('.fullname').text(memberName);
				viewObj.find('.position').text(memberPosition);
				viewObj.find('.profile').attr('href', memberProfile);
				viewObj.find('.contact').attr('href', memberContact);

				/*
				memberDesc = ;
				memberContact = ;
				memberProfile = 
				*/

				// move the view over the hook
				// hookOffset = memberHookObj.position();
				parentOffset = viewObj.parent().offset();
				hookOffset = memberHookObj.offset();
				//console.log(memberHookObj.position());
				//console.log(memberHookObj.offset());

				// console.log("before-shift (offset)" + JSON.stringify(hookOffset));
				hookOffset.top -= parentOffset.top;
				hookOffset.left -= parentOffset.left;

				// console.log("after-shift (offset)" + JSON.stringify(hookOffset));
				hookOffset.top += viewObj.height() / 2;
				hookOffset.left -= viewObj.width();

				viewObj.css(hookOffset);
				// console.log("final" + JSON.stringify(viewObj.offset()));

				// display the view
				viewObj.addClass('open-member');
			}, function () { // handlerOut
				viewObj.removeClass('open-member');
			});
	});

	//
	// Set up the slider
	//
	// enable lower slider
	$('*[data-toggle="i4p-memberlist-slider"]').each(function () {
		var memberSlider = this;
		//	viewId = $(this).attr('data-slider-view-id');

		// if (viewId === undefined) { console.error('data-slider-view-id not defined'); }

		// initialize the lower side (wide thumb slider with a 5-set list)
		$(memberSlider).anythingSlider({
			autoPlay: false,
			startStopped: true,

			buildArrows: true, // no prev/next arrows
			buildNavigation: true, // no tabs
			buildStartStop: false, // no start/stop
			hashTags: false,

			backText: " ", // "&lt;",
			forwardText: " ", // "&gt;",

			expand: false,
			resizeContents: false,
			showMultiple: 4,
			infiniteSlides: true, // no wrap
			changeBy: 4
		});
		jdebug('initialized bottom slider !');

	}); // lower slider init

});
