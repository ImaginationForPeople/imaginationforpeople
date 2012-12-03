
// require jquery

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

$(document).ready(function () {
	$('.comment-add .comment-new').keypress(function (ev) {
		var keycode = ev.keyCode || ev.which;
		if (keycode === 13 && !ev.shiftKey) {
			ev.preventDefault();
			this.form.submit();
		}
	});
});

