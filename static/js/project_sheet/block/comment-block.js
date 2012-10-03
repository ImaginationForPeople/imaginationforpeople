
$(document).ready(function() {
	$('.comment-add .comment-new').keypress(function(e) {
		var keycode = e.keyCode || e.which;
		if (keycode == 13 && !e.shiftKey) {
			e.preventDefault();
			this.form.submit();
		}
	});
});

