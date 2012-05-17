$(document).ready(function(){ 

        
    // Project slider buttons  
    $("#focus-nav .previous").click(function(){
        $('#projects_slide').data('AnythingSlider').goBack();
    });

    $("#focus-nav .next").click(function(){
        $('#projects_slide').data('AnythingSlider').goForward();
    });


    // Project slider nav
    $("#focus-menu .focus-filters a").click(function(){
        $("#focus-menu .focus-filters a").removeClass('selected');
        $(this).addClass('selected');
    });


});
