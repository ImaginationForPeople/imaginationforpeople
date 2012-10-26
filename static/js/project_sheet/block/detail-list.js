
// FIXME: add blue background effects on parent element of the editable content
$(document).ready(function(){
	$('.detail-item').each(function(){
		var itemThis = this;

		var editableThis = $(itemThis).find('.detail-answer');
		var editableTrigger = $(editableThis).attr('data-editable-trigger');

		$(editableThis).bind(editableTrigger,function(){
			// add edited class on elem
			$(itemThis).addClass('editing');
		});

		// FIXME: add onblur trigger for de-cssing
	});
});

