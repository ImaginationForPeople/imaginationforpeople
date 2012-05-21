$(document).ready(function(){ 

// Loginbox panels slide
    $("#loginbox .panel1 a#loginlink-subscribe").click(function () {
        $("#panels-slide").stop().animate({left: '-245px'}, 500);
    });	
    
    $("#loginbox .panel1 a.openid-button").click(function (){
        $("#panels-slide").stop().animate({left: '-490px'}, 500);
    });	
    
    $("#loginbox .loginpanel a.close-button").click(function (){
        $("#panels-slide").stop().animate({left: '0px'}, 500);
    });	
    
    
// Newsletter popup apparition
    $(window).bind('scroll', function(){
        if($(this).scrollTop() > 180) {
            $("#newsletter_popup").fadeIn(800, 0);
        }
    });
    

    
// Close button for newsletter popup
    $("#newsletter_popup .close-button").click(function (){
        $("#newsletter_popup").addClass("hidden");
    });	

});
