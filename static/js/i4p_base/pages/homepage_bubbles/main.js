$(document).ready(function(){
	 
	if(!Modernizr.touch){
		skrollr.init({
			forceHeight: false
		});
	
		$(".video").click(function() {
				$.fancybox({
					'padding'		: 0,
					'autoScale'		: false,
					'transitionIn'	: 'none',
					'transitionOut'	: 'none',
					'title'			: this.title,
					'width'			: '80%',
					'href'			: this.href.replace(new RegExp("watch\\?v=", "i"), 'v/'),
					'type'			: 'swf',
					'swf'			: {
					'wmode'				: 'transparent',
					'allowfullscreen'	: 'true'
					}
				});

				return false;
		});
	}
	
		
	// Set Header height to window height
	$("header").height( $( window ).height() - $("#main-nav-wr").height() );
	
	$("header").height( $( window ).height() );
	$("#intro > div").height( $( window ).height() - ($(".hello-bar").height() - 5) )
	
 	// Hello Bar	
	$(".hello-bar").delay(1000).slideDown();
	
	// Hello Bar
	$(".picto-close").click(function(){
	  	$(".hello-bar").slideUp();
	});
	
	// Delay to wait for hello bar
	setTimeout(function (){

		AdjustIntroHeight();

	}, 1000);	
	
	$( window ).resize(function() {
		AdjustIntroHeight();
	});
	
	function AdjustIntroHeight(){
		$("header").animate({
			height: $( window ).height() - ( $(".hello-bar").height() + 50 )
		}, 1000, function(){
		
		})
	
		$("#intro").animate({
			height: $( window ).height() - ($(".hello-bar").height() + 75 )
		}, 1000, function(){
		
		})
		
		$("#intro > div").height( $( window ).height() - ($(".hello-bar").height() - 5) )
	
	}

	// Nos applications button
	$("#nos-applications").hover(function(){
		$(this).children('span').animate({top: 100}
			, 300, function() {
				$(this).css('top','-100px').animate({top: 0}, 200)
			});
	})
	
	// Navigate to sections highlight on scroll
	var sections = $('[data-section]');
	$(window).scroll(function() {
	    var currentPosition = $(this).scrollTop();
	    sections.removeClass('selected').each(function() {
	        var top = $(this).offset().top,
	            bottom = top + $(this).height();
	        if (currentPosition >= top - $(this).height() / 2 && currentPosition <= bottom) {
				var index = $(this).attr('id');
				$('.controls ul a').removeClass('active');
				$('.controls ul a.' + index).first().addClass('active');
	        } 
	    });
	});
		
	// Naviagte to sections
	$('[data-section]').each(function(){
		$id = $(this).data('section'); 
		$label = $(this).data('section-name');
		$bouton = '<li><a href="#'+ $id +'" class="scrollTo '+ $id +'"><span>' + $label + '<span></span></span></a></li>';
		$('.controls ul').append($bouton);
	})
	
	$('.controls ul li').first().children('a').addClass('active'); 
	
	$('.controls ul li a').hover(
		function() {
			$(this).find('ul').children('a').removeClass('active');
		}, function() {
		
		}
	);
	
	$('.controls ul a').click(function(){
		$('.controls ul a').removeClass('active');
	})
	
	// Scroll to Animations
	$('.scrollTo, .arrow').click(function(){
		
		var scrollTo;
			
		if( $(this).attr('href') != undefined ){
			scrollTo = $(this).attr('href');
		} else if( $(this).data('scroll') != undefined ){
			scrollTo = '#' + $(this).data('scroll');
		} else { 
			//scrollTo = $(this).find('#main-content-wr').next('section').offset().top - $('header').height();
		}
				
		$(document).scrollTo( $(scrollTo) , 800, {easing: 'easeInOutExpo'} );
		return false;
			
	})
	
	
	
});  