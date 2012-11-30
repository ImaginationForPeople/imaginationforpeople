
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function () {
	$('.detail-item').each(function () {
		var itemThis = this,
			editableThis = $(itemThis).find('.detail-answer'),
			editableTrigger = $(editableThis).attr('data-editable-trigger');

		$(editableThis).bind(editableTrigger, function () {
			// add edited class on elem
			$(itemThis).addClass('editing');
		});

		// FIXME: add onblur trigger for de-cssing
	});
});

