
$(document).ready(function() {
	// we encapsulate editable call within each to force "this" to be correcly set...
	$("*[data-toggle='i4p-editable-button']").each(function(){
		$(this).click(function(e){
			e.preventDefault();
			var dataTarget = $(this).attr('data-target');
			$('#' + dataTarget).trigger("click");
		});
	});

	$("*[data-toggle='i4p-editable']").each(function(){
		$(this).editable($(this).attr('data-editable-save-url'), {
			tooltip: $(this).attr('data-editable-tooltip'),
			type: $(this).attr('data-editable-type'),
			loadurl: $(this).attr('data-editable-load-url'),
			loaddata: {
				'id' : $(this).attr('data-editable-id'),
				'language_code': $(this).attr('data-language-code')
			},
			submitdata: function(value, settings) {
				return {
					'id' : $(this).attr('data-editable-id'),
					'language_code': $(this).attr('data-language-code'),
					'description': '', 
					// FIXME: use the honeypot // $('.project_details_body input[name=description]').val()
				}
			},
			dataType: 'json',
			callback: function(data) {
				var res = jQuery.parseJSON(data);
				// FIXME: do CSS magic for current element type
				$(this).html(res.text);
			},
			indicator: 'Saving...',
			//cancel: '{% filter escapejs %}{% render_honeypot_field "description" %}{% endfilter %}<input title="{% trans "Cancel"|capfirst %}" class="r  edbutton right nomargin" style="margin-left:4px;" type="image" src="{{ STATIC_URL }}images/base/x.png" alt="Cancel"/>',
			cancel: 'Cancel',
			//submit: "<input title='{% trans 'Ok'|capfirst %}' class='greenbutton right nomargin' style='margin-left:4px;' type='image' src='{{ STATIC_U  RL }}images/base/v.png' alt='Ok'/>",
			submit: 'Save',
			onblur: 'ignore',
			cssclass: 'inline-edit',
			placeholder: $(this).attr('data-editable-tooltip')
		});

	});
});
