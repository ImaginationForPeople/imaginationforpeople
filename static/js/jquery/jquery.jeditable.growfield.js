$.editable.addInputType('growfield', {
    element : function(settings, original) {
        var textarea = $('<textarea>');
        if (settings.rows) {
            textarea.attr('rows', settings.rows);
        } else {
            textarea.height(settings.height);
        }
        if (settings.cols) {
            textarea.attr('cols', settings.cols);
        } else {
            textarea.width(settings.width);
        }
        // will execute when textarea is rendered
        textarea.ready(function() {
        });
        $(this).append(textarea);
        return(textarea);
    },
    plugin : function(settings, original) {
        // applies the growfield effect to the in-place edit field
        $('textarea', this).growfield(settings.growfield);
    }
});
