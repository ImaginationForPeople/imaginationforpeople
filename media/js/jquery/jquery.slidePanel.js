/* jQuery slidePanel plugin
 * Examples and documentation at: http://www.jqeasy.com/
 * Version: 1.0 (22/03/2010)
 * No license. Use it however you want. Just keep this notice included.
 * Requires: jQuery v1.3+
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */
(function($){
    $.fn.slidePanel = function(opts) {
        opts = $.extend({
            triggerName: '#trigger',
			position: 'absolute',
			triggerTopPos: '80px',
			panelTopPos: '50px',
			panelOpacity: 0.9,
            speed: 'fast',
			ajax: false,
			ajaxSource: null,
			clickOutsideToClose: true
        }, opts || {});
		
		var panel = this;
		var trigger = $(opts.triggerName);
		var isIE6 = $.browser.msie && $.browser.version=="6.0"
		
		// ie6 doesn't like fixed position
		if(isIE6) { opts.position = 'absolute' }
		// set css properties for trigger and panel
		trigger.css('position',opts.position)
		trigger.css('top',opts.triggerTopPos);
		panel.css('position',opts.position)
		panel.css('top',opts.panelTopPos);
		panel.css('filter', 'alpha(opacity='+(opts.panelOpacity*100)+')');
		panel.css('opacity', opts.panelOpacity);
		
		// triggerName mousedown event
		trigger.attr( "href", "javascript:void(0)" ).mousedown(function() {
			// load default content if ajax is false
			if (!opts.ajax) {
				panel.toggle(opts.speed);
				trigger.toggleClass("active");
			};
			// load ajax data if ajax is true or throw error if no ajaxSource defined
			if (opts.ajax && opts.ajaxSource!=null) {
				// fetch data ONLY when panel is hidden...
				// otherwise it fetches data when the panel is closing
				if (!panel.is(':visible')) {
					panel.load(opts.ajaxSource, function(response, status, xhr) {
						// if the ajax source wasn't loaded properly
						if (status !== "success") {
							var msg = "<p>Sorry, but there was an error loading the document.</p>";
							panel.html(msg);
						};
						// this is part of the .load() callback so it fills the panel BEFORE opening it
						panel.toggle(opts.speed);
					});
				} else {
					panel.toggle(opts.speed);
				};
				trigger.toggleClass("active");
			} else if (opts.ajax && opts.ajaxSource==null) {
					alert('You must define an ajaxSource to use Ajax.');
				};
			return false;
		});
	
		if (opts.clickOutsideToClose) {
			// bind the 'mousedown' event to the document so we can close panel without having to click triggerName
			$(document).bind('mousedown',function(){panel.hide(opts.speed);trigger.removeClass('active');});
			
			// don't close panel when clicking inside it
			panel.bind('mousedown',function(e){e.stopPropagation();});
		};
	};
})(jQuery);