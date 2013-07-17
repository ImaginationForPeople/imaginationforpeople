"use strict";

$(document).ready(function () {
	$('.infotable .map-button').click(function(){
		$('.infotable').fadeOut(300);
		$('.infolocationmap').fadeIn(300);
	});

	$('.infolocationmap .back').click(function(){
		$('.infotable').fadeIn(300);
		$('.infolocationmap').fadeOut(300);
	});

	if($('#gallery-modal-view-1 .video-item').length > 0) {
		index = $('#gallery-modal-view-1 .video-item:first').attr('data-slider-index');
		$('.links .video-link').attr('data-slider-index',index);
	} else {
		$('.links .video-link').hide();
	}
});