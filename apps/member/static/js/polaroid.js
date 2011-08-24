$(document).ready(function () { // When everything has loaded, place all polaroids on a random position	
    $(".polaroid").each(function () {
	
	var tempVal = Math.round(Math.random());
	if(tempVal == 1) {
	    var rotDegrees = randomXToY(350, 360); // rotate left
	} else {
	    var rotDegrees = randomXToY(0, 10); // rotate right
	}
	
	var position = $(this).parent().offset();
	var wiw = $(this).parent().width();
	var wih = $(this).parent().height();
	
	var leftpos = Math.random()*(wiw - $(this).width()) + position.left;
	var toppos = Math.random()*(wih - position.top) + position.top;
	var cssObj = { 'left' : leftpos,
		       'top' : toppos,
		       '-webkit-transform' : 'rotate('+ rotDegrees +'deg)',  // safari only
		       '-moz-transform' : 'rotate('+ rotDegrees +'deg)',  // firefox only
		       'tranform' : 'rotate('+ rotDegrees +'deg)' }; // added in case CSS3 is standard
	$(this).css(cssObj);
});
	
	// Set the Z-Index (used to display images on top while dragging)
	var zindexnr = 1;
	
	// boolean to check if the user is dragging
	var dragging = false;
	
	// Show the polaroid on top when clicked on
	$(".polaroid").mouseup(function(e){
		if(!dragging) {
			// Bring polaroid to the foreground
			zindexnr++;
			var cssObj = { 'z-index' : zindexnr,
			'transform' : 'rotate(0deg)',	 // added in case CSS3 is standard
			'-moz-transform' : 'rotate(0deg)',  // firefox only
			'-webkit-transform' : 'rotate(0deg)' };  // safari only
			$(this).css(cssObj);
		}
	});
	
	// Make the polaroid draggable & display a shadow when dragging
	$(".polaroid").draggable({
		containment: 'parent',
		cursor: 'crosshair',
		start: function(event, ui) {
			dragging = true;
			zindexnr++;
			var cssObj = { 'box-shadow' : '#888 3px 4px 4px', // added in case CSS3 is standard
				'-webkit-box-shadow' : '#888 3px 4px 4px', // safari only
				'-moz-box-shadow' : '#888 3px 4px 4px', // firefox only
				'padding-left' : '-4px',
				'padding-top' : '-4px',
				'z-index' : zindexnr };
			$(this).css(cssObj);
		},
		stop: function(event, ui) {
			var tempVal = Math.round(Math.random());
			if(tempVal == 1) {
				var rotDegrees = randomXToY(330, 360); // rotate left
			} else {
				var rotDegrees = randomXToY(0, 30); // rotate right
			}
			var cssObj = { 'box-shadow' : '', // added in case CSS3 is standard
				'-webkit-box-shadow' : '', // safari only
				'-moz-box-shadow' : '', // firefox only
				'transform' : 'rotate('+ rotDegrees +'deg)', // added in case CSS3 is standard
				'-webkit-transform' : 'rotate('+ rotDegrees +'deg)', // safari only
				'-moz-transform' : 'rotate('+ rotDegrees +'deg)', // firefox only
				'margin-left' : '0px',
				'margin-top' : '0px' };
			$(this).css(cssObj);
			dragging = false;
		}
	});
	
	// Function to get random number upto m
	// http://roshanbh.com.np/2008/09/get-random-number-range-two-numbers-javascript.html
	function randomXToY(minVal,maxVal,floatVal) {
		var randVal = minVal+(Math.random()*(maxVal-minVal));
		return typeof floatVal=='undefined'?Math.round(randVal):randVal.toFixed(floatVal);
	}
});