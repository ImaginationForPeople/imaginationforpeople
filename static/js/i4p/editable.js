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

// require jquery
// require jquery.editable

/*jslint browser: true*/
/*global $, jQuery, document*/

"use strict";

$(document).ready(function () {

	// we encapsulate editable call within each to force "this" to be correcly set...
	$("*[data-toggle='i4p-editable-button']").each(function () {
		var buttonThis = this,
			dataTarget = '#' + $(this).attr('data-target'),
			dataTargetTrigger = $(dataTarget).attr('data-editable-trigger');

		$(this).click(function (ev) {
			ev.preventDefault();
			$(dataTarget).trigger(dataTargetTrigger);
		});

		// hide clicked button and other for the same element once 
		// FIXME: hide other buttons for the same elements
		$(dataTarget).bind(dataTargetTrigger, function () {
			$(buttonThis).fadeOut('slow');
		});
	});

	$("*[data-toggle='i4p-editable']").each(function () {
		var editableThis = this,
			editableButtonEnableFn;

		editableButtonEnableFn = function () {
			// re-enable edit button
			$("*[data-toggle='i4p-editable-button']").each(function () {
				var buttonThis = this,
					buttonTarget = $(buttonThis).attr('data-target'),
					localId = $(editableThis).attr('id');

				//console.log("scanning button with target : #" + buttonTarget);

				if (localId === buttonTarget) {
					$(buttonThis).fadeIn('slow');
				}
			});
		};

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
				submitdata: function (value, settings) {
					return {
						'id' : $(editableThis).attr('data-editable-id'),
						'language_code': $(editableThis).attr('data-language-code'),
						'description': '',
						// FIXME: use the honeypot // $('.project_details_body input[name=description]').val()
					};
				},
				dataType: 'json',
				callback: function (data) {
					var res = jQuery.parseJSON(data);
					$(editableThis).html(res.text);
					editableButtonEnableFn();
					$(editableThis).trigger('submit');
				},
				indicator: 'Saving...',
				cancel: $(editableThis).attr('data-editable-cancel') || 'Cancel',
				submit: $(editableThis).attr('data-editable-submit') || 'Save',
				cssclass: 'inline-edit',
				placeholder: $(editableThis).attr('data-editable-tooltip'),
				onblur: 'ignore',
				onreset: function () {
					editableButtonEnableFn();
					$(editableThis).trigger('cancel');
				}
			}
		);
	});
});
