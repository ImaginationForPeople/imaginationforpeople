
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

// FIXME: change all i4p prefixes with a local i4p-block prefix (i4p-gallery_fancy_thin...)

"use strict";

$(document).ready(function () {

	var jdebug = function (str) { console.log('memberlist_modal: ' + str); };
	// var jdebug = function (str) { return null; };

	$('*[data-toggle="i4p-memberlist-modal-seeall"]').click(function (e) {
		var modalTargetId = $(this).attr('data-modal-target-id');

		if (modalTargetId === undefined) { console.error('data-modal-target-id not defined'); }

	//	jdebug('modal control called for slide ' + currentIndex + ' on ' + modalTargetId);
		$('#' + modalTargetId).modal();
		$('.modal-body .member-add-block').show();
	});

	jdebug('init DONE');

	$('.member-add-block form .action-close').click(function() {
		$(this).parents('.member-add-block').slideUp();
	});
});

