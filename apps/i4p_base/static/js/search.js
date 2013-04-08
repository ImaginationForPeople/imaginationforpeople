$(document).ready(function() {
	var request = null;

	// Text example for forms
	$(".search input[type=text]").example("{% trans 'Project search'|escapejs %}");

	var directives = {
		'li.projects ul li': {
			'project <- projects': { 
				'img@src': 'project.image',
				'a span': function(arg) { 
					return arg.item.title.substring(0, 30); 
				},
				'a@href': 'project.get_absolute_url'
			}
		},
		'li.projects@style': function(a) { return a.context.projects.length > 0 ? '':'display:none;' },
		'li.workgroups ul li': {
			'workgroup <- workgroups': {
				'a span': function(arg) { 
					return arg.item.name.substring(0, 30); 
				},
				'a@href': 'workgroup.get_absolute_url',
			}
		},
		'li.workgroups@style': function(a) { return a.context.workgroups.length > 0 ? '':'display:none;' },
		'li.profiles ul li': {
			'profile <- profiles': {
				'img@src': 'profile.mugshot',
				'a span': function(arg) { 
					return arg.item.get_full_name_or_username.substring(0, 30); 
				},
				'a@href': 'profile.get_absolute_url',
			}
		},
		'li.profiles@style': function(a) { return a.context.profiles.length > 0 ? '':'display:none;' }
	};

/* FIXME: warning: the following lines, if enabled, break the whole JS on the
 * site. There is obviously a bug in there.
 
	var q_template = $("#searchbox .q-suggestions-template").compile(directives);

	$(document).click(function() {
		$('#q-suggestions').hide();
	});

	var searchinput = $('#searchbox input[type=text]');

	searchinput.bind('keyup', 
		$.debounce(250, function() {
			if( $(this).val().length < 3 ) {
				// Hide the q-suggestions box
				$('#q-suggestions').hide();
			} else {
				// Show the AJAX Spinner
				searchinput.addClass('loading');

				// Cancel previous xhr if needed
				if ( request ) request.abort();

				request = $.ajax({
					url: i4p_globalsearch_complete_url,
					data: {"q": $(this).val() },
					success: function(data) {
						$("#q-suggestions ul").render(data, q_template)
						$("#q-suggestions").show();
						$("#q-suggestions ul").show();

						// Hide the AJAX Spinner
						searchinput.removeClass('loading');
					}
				});
			}
		}
		)
	); */
});
