$(document).ready(function(){ 

        
    // Login Slide opening
    $("#toppanel .open-panel").click(function(){
        $('#toppanel #panel').stop().animate({height : '190'}, "fast");
    });
    
    // Login Slide closing
    $("#toppanel").mouseleave(function(){    
        $(document).mousemove(function(e){
            if(e.pageY > 222){
                $('#toppanel #panel').stop().animate({height : '0'}, 100);
            } 
        }); 

        
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
    
    // Feedback tab
    var more = $('#feedback-tab textarea');
    more.hide();
    $('#feedback-tab #subject a.link').click(function() { more.fadeIn('fast'); });


    // Switch OpenID button to OpenID form in signin zone on click
    $(".social-panel a.openid-button").click(function () {
        $(".social-panel a.openid-button").hide();
        $(".social-panel .openid-form").removeClass('hidden');
    });	
        

    // Function opening of header's "hover menu"     
     function hovermenu(menu_item, hovermenu_zone, hovermenu_size){

        $(menu_item).find("a").hover(function(){
            $(this).parent("li").css('background-color', '#0f0f0f');
            $(hovermenu_zone).stop().animate({height : hovermenu_size}, "fast");
        }).mouseleave(function(){

            var hover_on = false;
            var hover_count = 150;
            
            setTimeout(myMouseOut, hover_count);

            $(hovermenu_zone).mouseover(function() {
                hover_on = true;
            });

            $(hovermenu_zone).mouseout(function() {
                hover_on = false;
                setTimeout(myMouseOut, hover_count);
            });
            
            $(menu_item).mouseover(function(){
                hover_on = true;
            });
            
            $(menu_item).mouseout(function(){
                hover_on = false;
                setTimeout(myMouseOut, hover_count);
            });

            function myMouseOut() {
                if (hover_on) {
                
                }else{
                    $(menu_item).css('background-color', 'transparent');
                    $(hovermenu_zone).stop().animate({height : '0'}, 100);
                }
            }

        });
    };
    
    //Initialization for header's "hover menus"
    hovermenu("#header #projects_list_button", '#projects-hover-menu-zone', '200');
    hovermenu("#header #about_button", '#about-hover-menu-zone', '50');
    
});
