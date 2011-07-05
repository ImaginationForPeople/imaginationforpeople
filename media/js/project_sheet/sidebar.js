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
		confirm("Are you sure to want to delete this member ? ", function () {
			console.log(link);
			window.location.href = link;
		});
	});
});
