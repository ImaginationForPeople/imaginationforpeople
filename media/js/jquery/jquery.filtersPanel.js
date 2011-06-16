$(document).ready(function(){ 
    $(".filters_box input.styled").ezMark();
    
    $(".filtersbox_content select#id_country").change(function(){
        $("#filter_form").submit();
    });
    
    $(".filters_box input.styled").change(function(){
        $("#filter_form").submit();
    });
    
    $(".tag_link").click(function(){
        var val = $("#id_themes").val();
        var tag_id = $(this).attr("id").replace("tag_", "");
        
        if($(this).hasClass("selected")){
            $(this).removeClass("selected");
            var new_val = val.replace(tag_id, "");
            new_val = new_val.replace(",,", ",");
            new_val = new_val.replace(/^,/g,'').replace(/,$/g,'')
            $("#id_themes").val(new_val);
        }
        else {
            $(this).addClass("selected");
            var new_tag = val == "" ? tag_id : ","+tag_id;
            $("#id_themes").val(val + new_tag);
        }
        $("#filter_form").submit();
    });

    $("#filters").toggle(function() {
        $('.categories_project_page').animate({height: '260px'});
        },
        function() {
        $('.categories_project_page').animate({height: '36px'});
        });
    }); 
          
          
$(document).ready(function() {
    $(".search #id_text").example("project search");
});
