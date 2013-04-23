$(document).ready(function(){ 
   //just to lock sliding panel
   $.cookie('i4p_bottom_panel', 'on', { expires: 1, path: '/'} );
     
   function refresh_results(){
   // Refresh search results by submitting form via Ajax call   
      var get_data = $("#filter_form").serialize();
      var callback_url = '/fr/project/list/?'+get_data;
      var updated_bar_url = callback_url // to update the bar url according to selected filters FIXME when a proper templating mechanism will be used with specific Json callback
    
      //$('div.content').load('/fr/project/list/?'+get_data+ ' div.content > *', function(){$("div.categories").unblock();});
      $.get(callback_url, function(data) {
         //replacing project listing
         var projects_list = $(data).find('#projects_list').children();
         $('#projects_list').empty().append(projects_list);
         //replacing paginations
         var pagination = $(data).find('div.projectlist_pagination').children();
         $('div.projectlist_pagination').empty().append(pagination[0]);
         
         // update URL
         var History = window.History; // Note: We are using a capital H instead of a lower h
         if ( !History.enabled ) {// History.js is disabled for this browser. This is because we can optionally choose to support HTML4 browsers or not.
            $("div.categories").unblock();
            return false;
         }
         History.pushState('', $('title').text(), updated_bar_url); // logs {state:3}, "State 3", "?state=3"
         
         // unblock flter panel
         $("div.categories").unblock();
      });
   
   }
  
  
   $(".filtersbox_content input.styled").ezMark();
    
   function blockPanel(){
    	$("div.categories").block({ message: '<h1>Filtering ...</h1>',
						    		css: { 
						                border: '1px solid #676665', 
						                padding: '15px', 
						                backgroundColor: '#000', 
						                opacity: .8,
						                color: '#fff' 
						            }});
    }
    
    $(".filtersbox_content select#id_country").change(function(){
    	blockPanel();
        //$("#filter_form").submit();
        refresh_results();
    });
    
    $(".filtersbox_content select#id_objectives").change(function(){
    	blockPanel();
        //$("#filter_form").submit();
        refresh_results();
    });
    
    $(".filters-picto input.styled").change(function(event){
    	blockPanel();
        //$("#filter_form").submit();
      refresh_results();
    });
    
    $(".filters-progress input").click(function(event){
        event.stopPropagation();
    });
    $('.filters-progress > ul > li')
    .css('cursor', 'pointer')
    .click(
      function(event){
          var checkBoxes = $(this).find('input');
          checkBoxes.attr("checked", !checkBoxes.attr("checked"));
          blockPanel();
          event.stopPropagation();
          //$("#filter_form").submit();
          refresh_results();
          //checkBoxes.trigger('click');
      }
    );
    
    $(".tag_link").click(function(){
    	blockPanel();
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
        //$("#filter_form").submit();
        refresh_results();
    });
   
    $("a#lock-picto").toggle(
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
    
    $('.categories_project_page .menu ul').idTabs();

    $(".search #id_text").example("Project Search");
    
    
});
