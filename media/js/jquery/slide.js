$(document).ready(function() {
	
	// Expand Panel
	$(".open-panel").click(function(){
		$("div#panel").slideDown("slow");	
	});	
	
	// Collapse Panel
	$(".close-panel").click(function(){
		$("div#panel").slideUp("slow");	
	});		
	
	// Switch buttons from "Log In | Register" to "Close Panel" on click
	$(".toggle a").click(function () {
		$(".toggle a").toggle();
	});		
		
});
