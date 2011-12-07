/*FIXME DUPLICATED CODE IN media.js */

function confirm(message, callback) {
	$('#confirm').modal({
		position: ["30%",],
		overlayId: 'confirm-overlay',
		containerId: 'confirm-container', 
		onShow: function (dialog) {
			var modal = this;

			$('.message', dialog.data[0]).append(message);
            
			$('.yes', dialog.data[0]).click(function () {
				if ($.isFunction(callback)) {
					callback.apply();
				}
				modal.close();
			});
			$('.no').click(function () {
				modal.close();
				return false;
			});
		}
	});
}


function showSidebar(aSidebar){
    /*$.blockUI({ message: null,
    	    	overlayCSS:  { 
    	            backgroundColor: '#000', 
    	            opacity:         0.6 
    	    	},
    	    	applyPlatformOpacityRules : false
    	      });*/
    aSidebar.css('visibility', 'visible');
    aSidebar.animate({'width': 760}, {
	duration: 450,
	step: function(now, fx) {
	    if(now > 400){
		aSidebar.find('form').fadeIn();
	    }
	}
    });
}

function hideSideBar(aSidebar){
    aSidebar.animate({'width': 260}, {
	duration: 450,
	step: function(now, fx) {
	    aSidebar.find('form').fadeOut();
	},
	complete: function() {
	    aSidebar.css('visibility', 'hidden');
	}
    });
    //$.unblockUI();
}

$(document).ready(function() {
    $('#opened-sidebar').css({'visibility': 'hidden','width': 260, 'height': 500});
    $('#opened-sidebar form').hide();
    
    $('#opened-sidebar-team').css({'visibility': 'hidden','width': 260, 'height': 350});
    $('#opened-sidebar-team form').hide();
    
    $('a.sidebar-opener.button').each(function(){
    	sidebar = $(this).attr("name");
	var top = $(this).parent().position().top;
    	if(top > 0){
    		  /* Remove the margin of the Team sidebar */
    	    top -= 15
    	}
    	$("#"+sidebar).css("top", top)
    });
    
    $('a.sidebar-opener').click(function() {
    	/* The name attribute of the anchor is the ID of the sidebar to open */
    	sidebar = $(this).attr("name");
    	showSidebar($("#"+sidebar));
    	return false;
    });
    
    $('a.sidebar-close').click(function() {
    	sidebar = $(this).parents(".grey_column_open");
    	hideSideBar(sidebar);
        return false;
    });
    
    
    $('#del_member_link').click(function (e) {
	e.preventDefault();
	var link = $(this).val();
	confirm("Are you sure to want to delete this member ?", function () {
	    window.location.href = link;
	});
    });
});

//
// Enable CSRF protection for AJAX requests
//
// Reference:
//    https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
//
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
