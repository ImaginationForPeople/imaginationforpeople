$(document).ready(function(){ 
   // mirror filter tags in URL to tag list
   rebuild_tag_list();
   
   function blockPanel(){
    	$("#col").block({ message: '<p>Filtering ...</p>',
						    		css: { 
						                border: '1px solid #676665', 
						                padding: '1px', 
						                backgroundColor: '#000', 
						                opacity: .6,
						                color: '#fff' 
						            }});
    }
   function refresh_results(){
   // Refresh search results by submitting form via Ajax call   
      blockPanel();
      var get_data = $("#search_form").serialize();
      var callback_url = $("#search_form").attr("action")+"?"+get_data;
      var updated_bar_url = callback_url; // to update the bar url according to selected filters FIXME when a proper templating mechanism will be used with specific Json callback
      $.get(callback_url, function(data) {
         //replacing project listing
         var projects_list = $(data).find('#projects-list').children();
         $('#projects-list').empty().append(projects_list);
         // update projects count
         $("#projects").empty().append($(data).find('#projects').children());
         // Update style for each element of class .hover
        $('.project-card .hover').hide();
         // update URL
         var History = window.History; // Note: We are using a capital H instead of a lower h
         if ( !History.enabled ) {// History.js is disabled for this browser. This is because we can optionally choose to support HTML4 browsers or not.
            return false;}
         History.pushState('', $('title').text(), updated_bar_url); // logs {state:3}, "State 3", "?state=3"
         $('#col').unblock();
      });
   }
   
   // ADDING TAGS to id_tags value attribute when entering text, separated by space
   $("#tag-search").keydown(function(e){if(e.keyCode == 13){e.preventDefault();}}); //prevent form submission
   $("#tag-search").keyup(function(event){
      if(event.keyCode == 13){
        event.preventDefault();//prevent form submission
        var tokens = $("#tag-search").val().toLowerCase().split(" ");              
        $.each(tokens, function(){
            var tmp = $('#id_tags').val();
            $('#id_tags').val($.trim(tmp+" "+this));
        });
        // empty text field and 
        $("#tag-search").val('');  
        rebuild_tag_list();
        refresh_results();
      }
   });
   // REMOVING TAGS from input and tag list when cliked
   $('#tags-list > ul > li > a').live('click', function(){
      var tag = $(this).text();
      console.log("removing :"+tag);
      var old_val = $('#id_tags').val().toLowerCase();
      var new_val = old_val.replace(tag,'');      
      $('#id_tags').val($.trim(new_val));
       rebuild_tag_list();
       refresh_results();
   });
   // REMOVING ALL TAGS
   $('#erase-tags').click(function(){
      $('#id_tags').val("");
      rebuild_tag_list();
   });
   // REBUILDING TAGS LIST with values in hidden input
   function rebuild_tag_list(){
      var tokens = $('#id_tags').val().toLowerCase().split(" ");
      // replace elements in tag lists
      $('#tags-list > ul').empty();
      $.each(tokens, function(){
            if (this.length > 0){
               console.log('= not space!= ');
               $('#tags-list > ul').append("<li><a href='javascript:;'>"+this.toLowerCase()+"</a></li>");
            }
       });
          
   }
   // LOCALISATION
   $('#id_country').attr('name', 'location'); // change name to match filter name FIXME
   $('#id_country').addClass("select");
   $('#id_country').change(function(){
      refresh_results();
   });
   
   //LANGUAGE
   $('#id_language').change(function(){
      refresh_results();
   });
   // Triger refresh when a checkbox is selected
   $('[type=checkbox]').click(function(event){
      console.log($("#search_form").serialize());
      refresh_results();
   
   });   
});
