"use strict";

$(document).ready(function () {

	$('#header #connect-block').hide();
	$('#header #me-block').hide();

   $(document).on('mouseenter', '#header #connect-link', function() {
      $(this).children('#connect-block').show();
   });
   $(document).on('mouseenter', '#header #me-link', function() {
      $(this).children('#me-block').show();
   });
   $(document).on('mouseleave', '#header #connect-block', function() {
      $(this).children('#connect-block').hide();
   });
   $(document).on('mouseleave', '#header #connect-link', function() {
      $(this).children('#connect-block').hide();
   });
   $(document).on('mouseleave', '#header #me-block', function() {
      $(this).children('#me-block').hide();
   });
   $(document).on('mouseleave', '#header #me-link', function() {
      $(this).children('#me-block').hide();
   });
});
