$(document).ready(function(){ 

        
    // Login Slide opening
    $("#toppanel .open-panel").click(function(){
        $('#toppanel #panel').stop().animate({height : '190'}, "fast");
    });
    
    $("#toppanel").mouseleave(function(){
        $('#toppanel #panel').stop().animate({height : '0'}, 100);
    });
    
		    
	 $('.tipsed').tipsy({gravity: $.fn.tipsy.autoNS, delayIn: 300});

         // Support panel
	  $('#feedback').slidePanel({
	      triggerName: '#feedback-trigger',
	      position: 'fixed',
	      triggerTopPos: '150px',
	      panelTopPos: '0px',
	      ajax: false
	  });
          var more = $('#feedback-tab textarea');
          more.hide();
          $('#feedback-tab #subject a.link').click(function() { more.fadeIn('fast'); });

      
      	// Switch OpenID button to OpenID form in signin zone on click
        $(".social-panel a.openid-button").click(function () {
            $(".social-panel a.openid-button").hide();
            $(".social-panel .openid-form").removeClass('hidden');
        });	
        

    // Opening of "projects hover menu"
        $("#header #projects_list_button").hover(function(){
        $(this).css('background-color', '#0f0f0f');
        $('#projects-hover-menu-zone').stop().animate({height : '200'}, "fast");
    }).mouseleave(function(){

        var hover_on = false;
        var hover_count = 150;
        
        setTimeout(myMouseOut, hover_count);

        $("#projects-hover-menu-zone").mouseover(function() {
            hover_on = true;
        });

        $("#projects-hover-menu-zone").mouseout(function() {
            hover_on = false;
            setTimeout(myMouseOut, hover_count);
        });
        
        $("#header #projects_list_button").mouseover(function(){
            hover_on = true;
        });
        
        $("#header #projects_list_button").mouseout(function(){
            hover_on = false;
            setTimeout(myMouseOut, hover_count);
        });

        function myMouseOut() {
            if (hover_on) {
            
            }else{
                $("#header #projects_list_button").css('background-color', 'transparent');
                $('#projects-hover-menu-zone').stop().animate({height : '0'}, 100);
            }
        }

    });


});
