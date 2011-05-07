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

/* Update the carousel so that it matches the current picture  */
function update_carousel(index) {
    var jcarousel = $('#project_photo_gallery_mini').data('jcarousel');
    
    if ( jcarousel.options.size > jcarousel.options.scroll )
    	jcarousel.scroll(index - 1, true);
}

/* When a thumbnail is clicked */
function changeslider(sid){
    var anyslider = $('#project_photo_gallery_current_photo');
    
    anyslider.anythingSlider(sid);
    update_carousel(sid);

    return false;
};

$(document).ready(function () {
    $('#project_photo_gallery_current_photo').find('embed[src*=youtube]').each(function(i) {
    	$(this).before('<param name="wmode" value="transparent">');
    	$(this).attr('wmode', "transparent");
    });

    $('#project_photo_gallery_current_photo > iframe').css('z-index', '-2000');

    $('#project_photo_gallery_current_photo').anythingSlider({
		width 				: 700,      	// Override the default CSS width
		height				: 460,			// Override the default CSS height
		delay               : 10000,      	// How long between slideshow transitions in AutoPlay mode (in milliseconds)
		animationTime       : 600,       	// How long the slideshow transition takes (in milliseconds)
		buildArrows         : false,      	// If true, builds the forwards and backwards buttons
		resizeContents      : true,      	// If true, solitary images/objects in the panel will expand to fit the viewport
		autoPlay            : false,     	// This turns off the entire slideshow FUNCTIONALY, not just if it starts running or not
		addWmodeToObject	: "transparent",
		easing				: 'easeInOutExpo'
    });	

    /* Disable callbacks on the buttons to set a new behaviour */
    $('#project_photo_gallery_mini').jcarousel({buttonNextEvent: null, buttonPrevEvent: null, wrap: 'circular', scroll: 4});
    
    var anyslider = $('#project_photo_gallery_current_photo').data('AnythingSlider');
    
    /* When the next button is clicked */
    $('.jcarousel-next').click(function() {
		anyslider.goForward();
		update_carousel(anyslider.currentPage);
    });
    
    /* When the previous button is clicked */
    $('.jcarousel-prev').click(function() {
    	anyslider.goBack();
		update_carousel(anyslider.currentPage);
    });
    
    var button = $('#media_metadata_button')
    $('.metadata').hide();

    button.hover(function() {
    		$('#all_metadata li:nth-child('+anyslider.currentPage+') div.metadata').fadeIn('fast');
    	}, 
	    function() {
    		$('#all_metadata li:nth-child('+anyslider.currentPage+') div.metadata').fadeOut('fast');
	    }
    );

    $('#del_media').click(function (e) {
		e.preventDefault();
		confirm("Are you sure to want to delete this media ? ", function () {
			window.location.href = anyslider.$currentPage.find('a.del_link').attr("href");
		});
	});
    
    $('ul#project_photo_gallery_current_photo').bind('slide_complete', function(){
    	var isImg = Boolean($(this).find("li.activePage").has("img.big-pic").length);
    
    	if(isImg){
    		button.unbind('click');
    		button.click(function(){
    			alert("Coming soon ...")
    			return false;
    		});
    	}
    	else {
    		button.unbind('click');
    		button.click(function(){
    			alert("TODO: Add a CSS class to gray out the button");
    			return false;
    		});
    	}
    });
    
    anyslider.gotoPage(1, false);
});
