/* Copyright (c) 2008 Jordan Kasper
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 * Copyright notice and license must remain intact for legal use
 * Requires: jQuery 1.2+
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS 
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN 
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * 
 * Fore more usage documentation and examples, visit:
 *          http://jkdesign.org/imagecheck/
 * 
 * Basic usage:
    <label for='someCheckbox'>Check it?</label>
    <input type='checkbox' id='someCheckbox' />
    
    $('#someCheckbox').simpleImageCheck({
      image: 'unchecked.png',             // String The image source to show when the checkbox IS NOT checked (REQUIRED) 
      imageChecked: 'checked.png',        // String The image source to show when the checkbox IS checked (REQUIRED)
      afterCheck: function(isChecked) {   // Function Optional callback function for when the image/checkbox is toggled
        // do something if isChecked === true
      }
    });
 * 
 * Note that when hovered, the image will have a class called 
 * imageCheckHover allowing you to alter its appearance if desired
 * 
 * TODO:
 *   Full testing suite
 *   tri/multi-state checkboxes
 *   broadcast hover events in addition to imageCheckHover class?
 * 
 * REVISIONS:
 *   0.1 Initial release
 *   0.2 Fix for keyboard navigation (thanks to allend for the tip)
 *   0.3 Took out unnecessary code
 *       Fixed issue with label clicking in some browsers
 *   0.4 Changed context of afterCheck callback to be the input node changed
 *       Added support for radio buttons
 */
;(function($) {
  
  $.fn.simpleImageCheck = function(o) {
    var n = this;
    if (n.length < 1) { return n; }
    
    // Set up options (and defaults)
    o = (o)?o:{};
    o = auditOptions(o);
    
    n.each(function() {
      var i = $(this);
      if (i.is(':checkbox') || i.is(':radio')) {
        setup(i, o);
      }
    });
    
    return n;
  };
  
  var setup = function(n, o) {
    var c = n.is(':checked');
    var src = o.image;
    if (c) { src = o.imageChecked; }
    
    // set id on input if it doesn't have one
    var id = n.attr('id');
    if (!id || id.length < 1) {
      id = n.attr('id', 'imageCheckInput_'+$.fn.simpleImageCheck.uid++).attr('id');
    }
    
    // we will use text of label for alt and title on image
    var l = $('label[for="'+id+'"]');
    
    // Create image node
    var im = n.before("<img src='"+src+"' id='ic_"+id+"' alt='"+l.text()+"' title='"+l.text()+"' class='imageCheck"+((c)?' checked':'')+"' role='checkbox' aria-checked='"+((c)?'true':'false')+"' aria-controls='"+id+"' />")
              .parent()
                .find('img#ic_'+id);
    
    n
      // attach handlers to the original input node to redirect to ours
      .click(function(e, triggered) {
        // Avoid infinite loop & double checking
        if (triggered === true) { return; }
        handleClick(n, im, o, true);
      })
      // Hide the original input box
      .hide();
    
    // IE doesn't fire click event on checkbox when label clicked
    l.click(function(e) {
      im.click(); // does double duty in all but IE
      return false;
    });
    
    // Unless the tab index is manually set, jQuery may not be able to 
    // get it using the attr() method, so we'll check multiple places
    // and then make sure its at least a number
    var ti = n.attr('tabindex') || n.get(0).tabIndex || 0;
    im
      // make image look 'clickable'
      .css({cursor: 'pointer'})
      // attach handlers to the image
      .click(function(e) {
        e.preventDefault();
        handleClick(n, im, o, false);
      })
      .keypress(function(e) {
        var k = (e.which)?e.which:((e.keyCode)?e.keyCode:0);
        // trigger on space or enter keys
        if (k == 13 || k == 32) {
          $(this).click();
        }
      })
      // add class to image on hover
      .hover(
        function() {
          $(this).addClass('imageCheckHover');
        },
        function() {
          $(this).removeClass('imageCheckHover');
        }
      )
      // set the tabIndex to make image focusable and enable key controls
      // we use DOM property versus jQuery because some older browsers
      // won't let you set the tabindex using the manner jQuery does
      .get(0).tabIndex = ti;
  }
  
  var handleClick = function(n, im, o, inputClick) {
    // determine if we need to check input box. i.e. if input is 
    // checked and img has 'checked' class, need to flip it
    if (im.hasClass('checked') === n.is(':checked') && !inputClick) {
      n.trigger('click', [true]).change();
    }
    // Now toggle the image source and change attributes to complete the ruse
    var c = n.is(':checked');
    im
      .toggleClass('checked')
      .attr({
        'aria-checked': ''+((c)?'true':'false'),
        'src': ''+((c)?o.imageChecked:o.image)
      });
    
    // Handle radio buttons
    if (n.is(':radio') && !inputClick) {
      $('input[name="'+n.attr('name')+'"]').not(n).each(function() {
        $('#ic_'+this.id)
          .removeClass('checked')
          .attr({
            'aria-checked': 'false',
            'src': ''+o.image
          });
      });
    }
    
    // Timeout to allow for 'checking' to occur before callback
    setTimeout(function() {  
      o.afterCheck.apply(n, [c]);
    }, 25);
  }
  
  // Defined outside simpleImageCheck to allow for usage during construction
  var auditOptions = function(o) {
    if (!$.isFunction(o.afterCheck)) { o.afterCheck = function() {}; }
    if (typeof(o.image) != 'string') { o.image = ''; }
    if (typeof(o.imageChecked) != 'string') { o.imageChecked = ''; }
    
    return o;
  }
  
  // Static properties
  $.fn.simpleImageCheck.uid = 0;
  
  
})(jQuery);