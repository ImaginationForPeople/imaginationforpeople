
/*jslint browser: true*/
/*global $, jQuery, document, console*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

(function () {
	"use strict";

	$(document).ready(function () {
		$('.project-toolbar ul li a').click(function () {
			var elemHref = $(this).attr('href'),
				targetSelector;

			targetSelector = 'a[name="' + elemHref.substr(1) + '"]';
			if ($(targetSelector).length > 0) {
				// console.log($(targetSelector));
				$('html, body').animate({
					scrollTop: $(targetSelector).offset().top
				});
			}
		});
	});
}());
