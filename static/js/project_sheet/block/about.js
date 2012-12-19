
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function () {
	// var jdebug = function (str) { console.log('about: ' + str); };
	var jdebug = function (str) { return null; };

	$('.project-about').has("*[data-toggle='i4p-editable']").each(function () {
		jdebug("each !");
		var itemThis = this,
			editableThis = $(itemThis).find("*[data-toggle='i4p-editable']"),
			editableTrigger = $(editableThis).attr('data-editable-trigger');

		$(editableThis).bind(editableTrigger, function () {
			// add edited class on elem
			$(itemThis).addClass('editing');
			jdebug('editing!');
		});

		$(editableThis).bind('submit', function () {
			// remove edited class on elem
			$(itemThis).removeClass('editing');
			jdebug('submit!');
		});

		$(editableThis).bind('cancel', function () {
			// remove edited class on elem
			$(itemThis).removeClass('editing');
			jdebug('cancel!');
		});
	});
});


