
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function () {
	$('.comment').each(function () {
		var itemThis = this,
			editableThis = $(itemThis).find('.comment-item'),
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

	$('.comment-form textarea').focus(function() {
		$(this).height('80px');
		$(this).css('line-height','1.5rem');
		$(this).css('padding-top','4px');
	});
	$('.comment-form textarea').blur(function() {
		$(this).height('26px');
		$(this).css('line-height','26px');
		$(this).css('padding-top','0');
	});
});
