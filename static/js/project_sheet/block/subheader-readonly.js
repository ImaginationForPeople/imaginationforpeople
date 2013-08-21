"use strict";

$(document).ready(function () {
   
	$('.infocard .back').click(function(){
		$('.infotable').fadeIn(300);
		$('#projectLocationsMap, .infocard a.back').css('display',  'none');
	});

	if($('#gallery-modal-view-1 .video-item').length > 0) {
	   console.log("There's videos!");
		var index = $('#gallery-modal-view-1 .video-item:first').attr('data-slider-index');
		$('.links .video-link').attr('data-slider-index',index);
	} else {
	   console.log("No video!");
		$('.links .video-link').hide();
	}
});
