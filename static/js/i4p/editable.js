
/*
 *
 * Assign jquery editable attributes on each dom object having the
 *
 *   data-trigger="editable"
 *
 * attribute.
 *
 * Thus object edition comportement is fully parametrable via HTML without
 * writing any javascript filling the following other attributes
 *
 * data-editable-tooltip : the tooltip to display on hover
 *   type: string
 *
 * data-editable-trigger : the trigger for editing element
 *   type: "click" | "dblclick" (default: click)
 *
 * data-editable-button :
 * data-editable-id : 
 * data-editable-load-url :
 * data-editable-save-url : 
 * data-editable-type : 
 *
*/

// FIXME: make sure jquery.editable plugin is loaded

$(document).ready(function() {

	// we encapsulate editable call within each to force "this" to be correcly set...
	$("*[data-toggle='i4p-editable-button']").each(function(){
		var buttonThis = this;
		var dataTarget = '#' + $(this).attr('data-target');
		var dataTargetTrigger = $(dataTarget).attr('data-editable-trigger');

		$(this).click(function(e){
			e.preventDefault();
			$(dataTarget).trigger(dataTargetTrigger);
		});

		// hide clicked button and other for the same element once 
		// FIXME: hide other buttons for the same elements
		$(dataTarget).bind(dataTargetTrigger, function() {
			$(buttonThis).fadeOut('slow');

		});
	});

	$("*[data-toggle='i4p-editable']").each(function(){
		var editableThis = this;

		$(this).editable(
			$(this).attr('data-editable-save-url'),
			{
				'event': $(editableThis).attr('data-editable-trigger'),
				tooltip: $(editableThis).attr('data-editable-tooltip'),
				type: $(editableThis).attr('data-editable-type'),
				loadurl: $(editableThis).attr('data-editable-load-url'),
				loaddata: {
					'id' : $(editableThis).attr('data-editable-id'),
					'language_code': $(editableThis).attr('data-language-code')
				},
				submitdata: function(value, settings) {
					return {
						'id' : $(editableThis).attr('data-editable-id'),
						'language_code': $(editableThis).attr('data-language-code'),
						'description': '',
						// FIXME: use the honeypot // $('.project_details_body input[name=description]').val()
					}
				},
				dataType: 'json',
				callback: function(data) {
					var res = jQuery.parseJSON(data);
					// FIXME: do CSS magic for current element type
					$(editableThis).html(res.text);
				},
				indicator: 'Saving...',
				//cancel: '{% filter escapejs %}{% render_honeypot_field "description" %}{% endfilter %}<input title="{% trans "Cancel"|capfirst %}" class="r  edbutton right nomargin" style="margin-left:4px;" type="image" src="{{ STATIC_URL }}images/base/x.png" alt="Cancel"/>',
				cancel: 'Cancel',
				//submit: "<input title='{% trans 'Ok'|capfirst %}' class='greenbutton right nomargin' style='margin-left:4px;' type='image' src='{{ STATIC_U  RL }}images/base/v.png' alt='Ok'/>",
				submit: 'Save',
				onblur: 'ignore',
				cssclass: 'inline-edit',
				placeholder: $(editableThis).attr('data-editable-tooltip'),
				onblur: function(data) {
					// re-enable edit button
					$("*[data-toggle='i4p-editable-button']").each(function(){
						var buttonThis = this;
						var buttonTarget = $(buttonThis).attr('data-target');
						var localId = $(editableThis).attr('id');
						//console.log("scanning button with target : #" + buttonTarget);

						if (localId == buttonTarget) {
							$(buttonThis).fadeIn('slow');
						}
					});
				}
			});
	});
});
