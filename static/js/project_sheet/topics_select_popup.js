// Rollover for topics selection popup
    $("#project_type .topic_picto").hover(function(){
        $(this).find('img').attr('src', $(this).find('img').attr('src').replace('.png', '-on.png'));
    }).mouseleave(function(){
        $(this).find('img').attr('src', $(this).find('img').attr('src').replace('-on-on.png', '.png'));
    });

    // Close button for new project topic popup
    $("#new_project_style_popup .close-button").click(function () {
        $("#new_project_style_popup_zone").addClass("hidden");
    });	
