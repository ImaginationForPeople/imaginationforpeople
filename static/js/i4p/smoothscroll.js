
/*jslint browser: true*/
/*global $, jQuery, document, console*/

// 
// Enable scrolling for anchor links having
// the data-toggle attribute set to i4p-smoothscroll.
//
// Ex: <a href="#somewhere" data-toggle="i4p-smoothscroll"> ... </a>
//

(function () {
	"use strict";

	$(document).ready(function () {
		$('[data-toggle="i4p-smoothscroll"]').click(function () {
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

