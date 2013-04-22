"use strict";

$(document).ready(function () {
	// COL
	$('#col section .inner').not(':first-child').hide();
	$('#col section header').click(function(){
		$(this).siblings('.inner').slideToggle();
	});
	$('.panel2').hide();
	$('#filter-button, #more-search .switch').click(function(){
		$('.panel1').slideUp(200, function(){
			$('.panel2').slideDown(600);
		});
		$('#filter-button').addClass('active');
		$('#discover-button').removeClass('active');
	});
	$('#discover-button').click(function(){
		$('.panel2').slideUp(200,function() {
			$('.panel1').slideDown(600);
		});
		$('#filter-button').removeClass('active');
		$('#discover-button').addClass('active');
	});

	// PROJECT CARD
	$('.project-card .hover').hide();
	//$('.project-card').on(
	//{  mouseenter : function(){
	//	   $(this).children('.hover').fadeIn(100);},
	//   mouseleave: function(){
	//	   $(this).children('.hover').fadeOut(100);}
	//});
	$(document).on('mouseenter', '.project-card', function() {
      $(this).children('.hover').fadeIn(100);
   });
   $(document).on('mouseleave', '.project-card', function() {
      $(this).children('.hover').fadeOut(100);
   });
	$('.project-card .hover').not('a').click(function(){
		window.location.href=$(this).children('.more').children('a').attr('href');
	});
});













































































































