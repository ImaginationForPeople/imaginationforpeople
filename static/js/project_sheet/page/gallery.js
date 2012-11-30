
// require jquery
// require jquery.anythingslider
// require jquery.anythingslider.fx

/*jslint browser: true*/
/*global $, jQuery, document*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

"use strict";

$(document).ready(function () {
	$('.subheader-actions .submit-button').click(function (ev) {
		alert('a malibu');
		console.log('get all forms & ajax validate');
		ev.preventDefault();
	});
});

