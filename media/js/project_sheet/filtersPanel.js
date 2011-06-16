$(document).ready(function(){ 
    $("ul.sf-menu").superfish({delay: 400, speed: 'fast'}); 
    
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
    
    $("div.categories_project_page .categ-button a").click(function(){
    	$("div.categories_project_page .categ-button").removeClass("selected");
    	$("div.categories_project_page .categ-panel").hide();
    	
    	var tab = $(this).parent();
    	var panel = $("div.categories_project_page div#projects_"+ tab.attr("id"));
    	
    	tab.addClass("selected");
    	panel.show();
    });
   
    $("div#lock-picto").toggle(
    	function () {
    		$(this).removeClass("off");
    		$(this).addClass("on");
    		$.cookie('i4p_bottom_panel', 'on', { expires: 1, path: '/'} );
    		
    	},
		function () {
		      $(this).removeClass("on");
		      $(this).addClass("off");
		      $.cookie('i4p_bottom_panel', null, { expires: -1, path: '/' } );
		}
      );
    
    if($.cookie('i4p_bottom_panel') == 'on'){
    	$("div#lock-picto").click();
    	$(".categories_project_page").animate({height: '260px'}); 
    }
    
    $(".categories_project_page").hoverIntent({    
	     over: function() {
	    	 if($.cookie('i4p_bottom_panel') != 'on'){
	    		 $(".categories_project_page").animate({height: '260px'});
	    	 }
	     },
	     timeout: 200,
	     out: function() { 
	    	 if($.cookie('i4p_bottom_panel') != 'on'){
	    		 $(".categories_project_page").animate({height: '36px'});
	    	 }
	     },  
	});
    
    $("div.categories_project_page .selected > a").click();

});
  
$(document).ready(function() {
    $(".search #id_text").example("project search");
});
