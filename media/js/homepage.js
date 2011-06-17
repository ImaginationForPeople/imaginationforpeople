(function($) {
    $.fn.mosaic = function() {

	var project_items_container = $('ul#projects_rotator');

	var project_items = project_items_container.children('li');
	var project_thumbs_container = $(this);

	var previous_item = null; // previously displayed
	var current_item = null; // latest selected
	var hovered_item = null; // hovered

	var item_count = $(project_items).length;

	var block_rotator = false;

	project_items.children().hide();
	
	var init_delay = 2000;
	var rotator_delay = 6000;
	
	$(this).oneTime(init_delay, 'for', function() {
	    $('#for-picto').fadeOut('slow');
	});
	scheduleRotatorFirstRun(init_delay, rotator_delay);

	//--------------------

	function scheduleRotatorFirstRun(first_delay, delay) {
	    $(this).oneTime(first_delay, 'rot_first', function(i) {
		switchToRandom();
		scheduleRotator(delay);
	    })
	}

	function scheduleRotator(delay) {
	    $(project_items_container).everyTime(delay, 'rotator', function(i) {
		switchToRandom();
	    })
	}

	function switchToRandom() {
	    if ( block_rotator )
		return;

	    if ( item_count == 0 )
		return;

	    do {
		var random_index = Math.floor(Math.random()*item_count)
		selected_item = project_items.get(random_index);
	    } while ( selected_item == current_item  )
	    
	    switchTo(random_index);
	}

	function stopRotator() {
	    $(project_items_container).stopTime();	    
	}


	function setCurrent(idx) {
	    if ( current_item ) {
		$(current_item).removeClass('current');
	    }

	    previous_item = current_item;

	    $(project_thumbs_container).children().removeClass('selected');
	    $(project_thumbs_container.children().get(idx)).addClass('selected');
	    $(this).addClass('selected');
	    current_item = project_items.get(idx);

	    $(current_item).addClass('current');
	}

	function hideCurrent() {
	    var picture = $(current_item).children('img');
	    var scroll = $(current_item).children('div.project_desc');

	    $(scroll).stop().css('z-index', '9').animate({right: '-266', opacity: '0.2'}, 600, function() { $(this).hide(); });
	    $(picture).stop().animate({'opacity': '0.5'}, 600); //, function() { $(this).hide(); });

	}

	function showCurrent() {
	    var picture = $(current_item).children('img');
	    var scroll = $(current_item).children('div.project_desc');

	    var previous_picture = $(previous_item).children('img');

	    $(previous_picture).promise().done(function() {
		$(previous_picture).animate({'opacity': '0.0'}, 600, function() { $(this).hide(); });
		$(picture).stop().show().css('opacity', '0.2').animate({opacity: '1.0'}, 600);
	    });


	    $(scroll).stop().show().animate({right: '266', opacity: '0.90'}, 800, function() {
		$(this).css('z-index', '110')
	    });
	}

	function switchTo(index) {
	    hideCurrent();
	    setCurrent(index);
	    showCurrent();
	}

	this.children('li').hoverIntent(function(e) {
	    $(this).addClass('hovered');

	    block_rotator = true;

	    var idx = $(this).index();

	    hovered_item = project_items.get(idx);

	    if ( hovered_item == current_item )
		return false;

	    switchTo(idx);

	}, function(e) {
	    $(this).removeClass('hovered');
	    hovered_item = null;
	})

	this.hover(function() {}, function() {
	    block_rotator = false;
	})

	project_items.children('.project_desc').hover(function() {
	    block_rotator = true;
	}, function() {
	    block_rotator = false;
	})

    }
})( jQuery );