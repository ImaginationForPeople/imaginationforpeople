"use strict";

// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function () {
	var hSize = $('#new_project_style_popup_zone').outerHeight() + $('#header-zone').outerHeight() + $('.project-subheader').outerHeight();
	$(window).bind('scroll', function() {
         if ($(window).scrollTop() > hSize ) {
             $('.project-menubar').addClass('fixed');
         }
         else {
             $('.project-menubar').removeClass('fixed');
         }
    });
});