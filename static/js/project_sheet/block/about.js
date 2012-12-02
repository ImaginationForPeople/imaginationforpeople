
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function () {
	$('.project-about').each(function () {
		var itemThis = this,
			editableThis = $(itemThis).find("*[data-toggle='i4p-editable']"),
			editableTrigger = $(editableThis).attr('data-editable-trigger');

		$(editableThis).bind(editableTrigger, function () {
			// add edited class on elem
			$(itemThis).addClass('editing');
		});

		$(editableThis).bind('submit', function () {
			// remove edited class on elem
			$(itemThis).removeClass('editing');
		});

		$(editableThis).bind('cancel', function () {
			// remove edited class on elem
			$(itemThis).removeClass('editing');
		});
	});
});


