"use strict";

$(document).ready(function () {
	// COL
	$('#col section .inner').not(':first-child').hide();
	$('#col section header h1').click(function(){
		$(this).parent('header').siblings('.inner').slideToggle();
	});
	$('.panel1').hide();
	$('#filter-button, #more-search .switch').click(function(){
		$('.panel2').slideUp(200, function(){
			$('.panel1').slideDown(600);
		});
		$('#filter-button').addClass('active');
		$('#discover-button').removeClass('active');
	});
	$('#discover-button').click(function(){
		$('.panel1').slideUp(200,function() {
			$('.panel2').slideDown(600);
		});
		$('#filter-button').removeClass('active');
		$('#discover-button').addClass('active');
	});
});
