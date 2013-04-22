$(document).ready(function(){ 
     
   function refresh_results(){
   // Refresh search results by submitting form via Ajax call   
      var get_data = $("#search_form").serialize();
      var callback_url = $("#search_form").attr("action")+"?"+get_data;
      var updated_bar_url = callback_url; // to update the bar url according to selected filters FIXME when a proper templating mechanism will be used with specific Json callback
    
      //$('div.content').load('/fr/project/list/?'+get_data+ ' div.content > *', function(){$("div.categories").unblock();});
      $.get(callback_url, function(data) {
         //replacing project listing
         var projects_list = $(data).find('#projects-list').children();
         $('#projects-list').empty().append(projects_list);
         // update projects count
         $("#projects").empty().append($(data).find('#projects').children());
         // Update style for each element of class .hover
         $('.project-card .hover').hide();
        // $('.hover').each(function(){
          //   console.log("==changing===");
            // $(this).attr('style', 'display : none;');
         //});
         //$('.hover').attr('style', 'display : none;');
         //replacing paginations
         //var pagination = $(data).find('div.projectlist_pagination').children();
         //$('div.projectlist_pagination').empty().append(pagination[0]);
         
         // update URL
         var History = window.History; // Note: We are using a capital H instead of a lower h
         if ( !History.enabled ) {// History.js is disabled for this browser. This is because we can optionally choose to support HTML4 browsers or not.
            return false;
         }
         History.pushState('', $('title').text(), updated_bar_url); // logs {state:3}, "State 3", "?state=3"
         
      });
   }
   
   // add tags filter to id_tags value attribute when entering text, separated by space
   $("#tag-search").keydown(function(e){if(e.keyCode == 13){e.preventDefault();}}); //prevent form submission
   $("#tag-search").keyup(function(event){      
      if(event.keyCode == 13){
        event.preventDefault();//prevent form submission
        var tokens = $("#tag-search").val().split(" ");        
        $.each(tokens, function(){
            // add each token in tag lists
            console.log(this);
            $('#tags-list > ul').append("<li><a href='javascript:;'>"+this+"</a></li>");
            // add each token to value attr of tags input, TODO: checking for duplicates
            var tmp = $('#id_tags').val();
            $('#id_tags').val(tmp+" "+this);
            // empty text field
            $("#tag-search").val('');
        });
      }
   });
   // TODO remove tag from input and tag list when cliked
   // TODO mirror tags-list with values in id_tags hidden input
   function mirror_tag_values(){
      // reads values
      // replace elements in tag lists
   
   }
   
   // Triger refresh when a checkbox is selected
   $('[type=checkbox]').click(function(event){
      console.log($("#search_form").serialize());
      refresh_results();
   
   });
   
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
  
    $(".search #id_text").example("Project Search");
    
    
});
