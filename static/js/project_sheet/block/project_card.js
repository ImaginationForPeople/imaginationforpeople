"use strict";

$(document).ready(function () {
	// PROJECT CARD
	$('.project-card .hover').hide();
	//$('.project-card').on(
	//{  mouseenter : function(){
	//	   $(this).children('.hover').fadeIn(100);},
	//   mouseleave: function(){
	//	   $(this).children('.hover').fadeOut(100);}
	//});
	$(document).on('mouseenter', '.project-card .top', function() {
      $(this).siblings('.hover').fadeIn(100);
   });
   $(document).on('mouseleave', '.project-card .hover', function() {
      $(this).fadeOut(100);
   });
	$('.project-card .hover').not('a').click(function(){
		window.location.href=$(this).children('.more').children('a').attr('href');
	});
});