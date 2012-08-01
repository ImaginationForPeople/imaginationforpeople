//var $, scriptUrl, askbotSkin
/**
 * attention - this function needs to be retired
 * as it cannot accurately give url to the media file
 */
var mediaUrl = function(resource){
    return askbot['settings']['static_url'] + 'default' + '/' + resource;
};

var cleanUrl = function(url){
    var re = new RegExp('//', 'g');
    return url.replace(re, '/');
};

var copyAltToTitle = function(sel){
    sel.attr('title', sel.attr('alt'));
};

var animateHashes = function(){
    var id_value = window.location.hash;
    if (id_value != ""){
        var previous_color = $(id_value).css('background-color');
        $(id_value).css('backgroundColor', '#FFF8C6');
        $(id_value)
            .animate({backgroundColor: '#ff7f2a'}, 500)
            .animate({backgroundColor: '#FFF8C6'}, 500, function(){
                $(id_value).css('backgroundColor', previous_color);
            });
    }
};

var getUniqueWords = function(value){
    var words = $.trim(value).split(/\s+/);
    var uniques = new Object();
    var out = new Array();
    $.each(words, function(idx, item){
        if (!(item in uniques)){
            uniques[item] = 1;
            out.push(item);
        };
    });
    return out;
};

var showMessage = function(element, msg, where) {
    var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(' +
    gettext('click to close') + ')</div>');

    div.click(function(event) {
        $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
    });

    var where = where || 'parent';

    if (where == 'parent'){
        element.parent().append(div);
    }
    else {
        element.after(div);
    }

    div.fadeIn("fast");
};

//outer html hack - https://github.com/brandonaaron/jquery-outerhtml/
(function($){
    var div;
    $.fn.outerHTML = function() {
        var elem = this[0],
        tmp;
        return !elem ? null
        : typeof ( tmp = elem.outerHTML ) === 'string' ? tmp
        : ( div = div || $('<div/>') ).html( this.eq(0).clone() ).html();
    };
})(jQuery);

var makeKeyHandler = function(key, callback){
    return function(e){
        if ((e.which && e.which == key) || (e.keyCode && e.keyCode == key)){
            if(!e.shiftKey){
                callback();
                return false;
            }
        }
    };
};


var setupButtonEventHandlers = function(button, callback){
    button.keydown(makeKeyHandler(13, callback));
    button.click(callback);
};


var putCursorAtEnd = function(element){
    var el = element.get()[0];
    if (el.setSelectionRange){
        var len = element.val().length * 2;
        el.setSelectionRange(len, len);
    }
    else{
        element.val(element.val());
    }
    element.scrollTop = 999999;
};

var setCheckBoxesIn = function(selector, value){
    return $(selector + '> input[type=checkbox]').attr('checked', value);
};

var notify = function() {
    var visible = false;
    return {
        show: function(html) {
            if (html) {
                $("body").addClass('user-messages');
                $(".notify span").html(html);        
            }          
            $(".notify").fadeIn("slow");
            visible = true;
        },       
        close: function(doPostback) {
            /*if (doPostback) {
               $.post(
                   askbot['urls']['mark_read_message'],
                   { formdata: "required" }
               );
            }*/
            $(".notify").fadeOut("fast");
            $('body').removeClass('user-messages');
            visible = false;
        },     
        isVisible: function() { return visible; }     
    };
} ();

/* **************************************************** */
// Search query-string manipulation utils
/* **************************************************** */

var QSutils = QSutils || {};  // TODO: unit-test me

QSutils.TAG_SEP = ','; // should match const.TAG_SEP; TODO: maybe prepopulate this in javascript.html ?

QSutils.get_query_string_selector_value = function (query_string, selector) {
    var params = query_string.split('/');
    for(var i=0; i<params.length; i++) {
        var param_split = params[i].split(':');
        if(param_split[0] === selector) {
            return param_split[1];
        }
    }
    return undefined;
};

QSutils.patch_query_string = function (query_string, patch, remove) {
    var params = query_string.split('/');
    var patch_split = patch.split(':');

    var new_query_string = '';
    var mapping = {};

    if(!remove) {
        mapping[patch_split[0]] = patch_split[1]; // prepopulate the patched selector if it's not meant to be removed
    }

    for (var i = 0; i < params.length; i++) {
        var param_split = params[i].split(':');
        if(param_split[0] !== patch_split[0] && param_split[1]) {
            mapping[param_split[0]] = param_split[1];
        }
    }

    var add_selector = function(name) {
        if(name in mapping) {
            new_query_string += name + ':' + mapping[name] + '/';
        }
    };

    /* The order of selectors should match the Django URL */
    add_selector('scope');
    add_selector('sort');
    add_selector('query');
    add_selector('tags');
    add_selector('author');
    add_selector('page');

    return new_query_string;
};

QSutils.remove_search_tag = function(query_string, tag){
    var tag_string = this.get_query_string_selector_value(query_string, 'tags');
    if(!tag_string) {
        return query_string;
    }

    var tags = tag_string.split(this.TAG_SEP);

    var pos = $.inArray(encodeURIComponent(tag), tags);
    if(pos > -1) {
        tags.splice(pos, 1); /* array.splice() works in-place */
    }

    if(tags.length === 0) {
        return this.patch_query_string(query_string, 'tags:', true);
    } else {
        return this.patch_query_string(query_string, 'tags:' + tags.join(this.TAG_SEP));
    }
};

QSutils.add_search_tag = function(query_string, tag){
    var tag_string = this.get_query_string_selector_value(query_string, 'tags');
    tag = encodeURIComponent(tag);
    if(!tag_string) {
        tag_string = tag;
    } else {
        tag_string = [tag_string, tag].join(this.TAG_SEP);
    }

    return this.patch_query_string(query_string, 'tags:' + tag_string);
};

/* **************************************************** */

/* some google closure-like code for the ui elements */
var inherits = function(childCtor, parentCtor) {
  /** @constructor taken from google closure */
    function tempCtor() {};
    tempCtor.prototype = parentCtor.prototype;
    childCtor.superClass_ = parentCtor.prototype;
    childCtor.prototype = new tempCtor();
    childCtor.prototype.constructor = childCtor;
};

/* wrapper around jQuery object */
var WrappedElement = function(){
    this._element = null;
    this._in_document = false;
};
WrappedElement.prototype.setElement = function(element){
    this._element = element;
};
WrappedElement.prototype.createDom = function(){
    this._element = $('<div></div>');
};
WrappedElement.prototype.decorate = function(element){
    this._element = element;
};
WrappedElement.prototype.getElement = function(){
    if (this._element === null){
        this.createDom();
    }
    return this._element;
};
WrappedElement.prototype.inDocument = function(){
    return this._in_document;
};
WrappedElement.prototype.enterDocument = function(){
    return this._in_document = true;
};
WrappedElement.prototype.hasElement = function(){
    return (this._element !== null);
};
WrappedElement.prototype.makeElement = function(html_tag){
    //makes jQuery element with tags
    return $('<' + html_tag + '></' + html_tag + '>');
};
WrappedElement.prototype.dispose = function(){
    this._element.remove();
    this._in_document = false;
};

/**
 * Can be used for an input box or textarea.
 * The original value will be treated as an instruction.
 * When user focuses on the field, the tip will be gone,
 * when the user escapes without typing anything besides 
 * perhaps empty text, the instruction is restored.
 * When instruction is shown, class "blank" is present
 * in the input/textare element.
 */
var TippedInput = function(){
    WrappedElement.call(this);
    this._instruction = null;
};
inherits(TippedInput, WrappedElement);

TippedInput.prototype.reset = function(){
    $(this._element).val(this._instruction);
    $(this._element).addClass('blank');
};

TippedInput.prototype.isBlank = function(){
    return this.getVal() === this._instruction;
};

TippedInput.prototype.getVal = function(){
    return this._element.val();
};

TippedInput.prototype.setVal = function(value){
    if (value) {
        this._element.val(value);
        if (this.isBlank()){
            this._element.addClass('blank');
        } else {
            this._element.removeClass('blank');
        }
    }
};

TippedInput.prototype.decorate = function(element){
    this._element = element;
    var instruction_text = this.getVal();
    this._instruction = instruction_text;
    this.reset();
    var me = this;
    $(element).focus(function(){
        if (me.isBlank()){
            $(element)
                .val('')
                .removeClass('blank');
        }
    });
    $(element).blur(function(){
        var val = $(element).val();
        if ($.trim(val) === ''){
            $(element)
                .val(instruction_text)
                .addClass('blank');
        }
    });
    makeKeyHandler(13, function(){
        $(element).blur();
    });
};

/**
 * will setup a bootstrap.js alert
 * programmatically
 */
var AlertBox = function(){
    WrappedElement.call(this);
    this._text = null;
};
inherits(AlertBox, WrappedElement);

AlertBox.prototype.setClass = function(classes){
    this._classes = classes;
    if (this._element){
        this._element.addClass(classes);
    }
};

AlertBox.prototype.setError = function(state){
    this._is_error = state;
    if (this._element) {
        if (state === true) {
            this._element.addClass('alert-error');
        } else {
            this._element.removeClass('alert-error');
        }
    }
};

AlertBox.prototype.setText = function(text){
    this._text = text;
    if (this._content){
        this._content.html(text);
    }
};

AlertBox.prototype.getContent = function(){
    if (this._content){
        return this._content;
    } else {
        this._content = this.makeElement('div');
        return this._content;
    }
};

AlertBox.prototype.setContent = function(content){
    var container = this.getContent();
    container.empty()
    container.append(content);
};

AlertBox.prototype.addContent = function(content){
    var container = this.getContent();
    container.append(content);
};

AlertBox.prototype.createDom = function(){
    this._element = this.makeElement('div');
    this._element.addClass('alert fade in');

    if (this._is_error) {
        this.setError(this._is_error);
    }

    if (this._classes){
        this._element.addClass(this._classes);
    }

    this._cancel_button = this.makeElement('button');
    this._cancel_button
        .addClass('close')
        .attr('data-dismiss', 'alert')
        .html('&times;');
    this._element.append(this._cancel_button);

    this._element.append(this.getContent());
    if (this._text){
        this.setText(this._text);
    }

    this._element.alert();//bootstrap.js alert
};

var SimpleControl = function(){
    WrappedElement.call(this);
    this._handler = null;
    this._title = null;
};
inherits(SimpleControl, WrappedElement);

SimpleControl.prototype.setHandler = function(handler){
    this._handler = handler;
    if (this.hasElement()){
        this.setHandlerInternal();
    }
};

SimpleControl.prototype.getHandler = function(){
    return this._handler;
};

SimpleControl.prototype.setHandlerInternal = function(){
    //default internal setHandler behavior
    setupButtonEventHandlers(this._element, this._handler);
};

SimpleControl.prototype.setTitle = function(title){
    this._title = title;
};

var EditLink = function(){
    SimpleControl.call(this)
};
inherits(EditLink, SimpleControl);

EditLink.prototype.createDom = function(){
    var element = $('<a></a>');
    element.addClass('edit');
    this.decorate(element);
};

EditLink.prototype.decorate = function(element){
    this._element = element;
    this._element.attr('title', gettext('click to edit this comment'));
    this._element.html(gettext('edit'));
    this.setHandlerInternal();
};

var DeleteIcon = function(title){
    SimpleControl.call(this);
    this._title = title;
    this._content = null;
};
inherits(DeleteIcon, SimpleControl);

DeleteIcon.prototype.decorate = function(element){
    this._element = element;
    this._element.attr('class', 'delete-icon');
    this._element.attr('title', this._title);
    if (this._handler !== null){
        this.setHandlerInternal();
    }
};

DeleteIcon.prototype.setHandlerInternal = function(){
    setupButtonEventHandlers(this._element, this._handler);
};

DeleteIcon.prototype.createDom = function(){
    this._element = this.makeElement('span');
    this.decorate(this._element);
    if (this._content !== null){
        this.setContent(this._content);
    }
};

DeleteIcon.prototype.setContent = function(content){
    if (this._element === null){
        this._content = content;
    } else {
        this._content = content;
        this._element.html(content);
    }
}

/**
 * attaches a modal menu with a text editor
 * to a link. The modal menu is from bootstrap.js
 */
var TextPropertyEditor = function(){
    WrappedElement.call(this);
    this._editor = null;
};
inherits(TextPropertyEditor, WrappedElement);

TextPropertyEditor.prototype.getWidgetData = function(){
    var data = this._element.data();
    return {
        object_id: data['objectId'],
        model_name: data['modelName'],
        property_name: data['propertyName'],
        url: data['url'],
        help_text: data['helpText'],
        editor_heading: data['editorHeading']
    };
};

TextPropertyEditor.prototype.makeEditor = function(){
    if (this._editor) {
        return this._editor;
    }
    var editor = this.makeElement('div')
        .addClass('modal');
    this._editor = editor;

    var header = this.makeElement('div')
        .addClass('modal-header');
    editor.append(header);

    var close_link = this.makeElement('div')
        .addClass('close')
        .attr('data-dismiss', 'modal')
        .html('x');
    header.append(close_link);

    var title = this.makeElement('h3')
        .html(this.getWidgetData()['editor_heading']);
    header.append(title);

    var body = this.makeElement('div')
        .addClass('modal-body');
    editor.append(body);

    var textarea = this.makeElement('textarea')
        .addClass('tipped-input blank')
        .val(this.getWidgetData()['help_text']);
    body.append(textarea);

    var tipped_input = new TippedInput();
    tipped_input.decorate(textarea);
    this._text_input = tipped_input;

    var footer = this.makeElement('div')
        .addClass('modal-footer');
    editor.append(footer);

    var save_btn = this.makeElement('button')
        .addClass('btn btn-primary')
        .html(gettext('Save'));
    footer.append(save_btn);

    var cancel_btn = this.makeElement('button')
        .addClass('btn cancel')
        .html(gettext('Cancel'));
    footer.append(cancel_btn);

    var me = this;
    setupButtonEventHandlers(save_btn, function(){
        me.saveData();
    });
    setupButtonEventHandlers(cancel_btn, function(){
        editor.modal('hide');
    });
    editor.modal('hide');

    $(document).append(editor);
    return editor;
};

TextPropertyEditor.prototype.openEditor = function(){
    this._editor.modal('show');
};

TextPropertyEditor.prototype.clearMessages = function(){
    this._editor.find('.alert').remove();
};

TextPropertyEditor.prototype.getAlert = function(){
    var box = new AlertBox();
    var modal_body = this._editor.find('.modal-body');
    modal_body.prepend(box.getElement());
    return box;
};

TextPropertyEditor.prototype.showAlert = function(text){
    this.clearMessages();
    var box = this.getAlert();
    box.setText(text);
    return box;
};

TextPropertyEditor.prototype.showError = function(text){
    var box = this.showAlert(text);
    box.setError(true);
    return box;
};

TextPropertyEditor.prototype.setText = function(text){
    this._text_input.setVal(text);
};

TextPropertyEditor.prototype.getText = function(){
    return this._text_input.getVal();
};

TextPropertyEditor.prototype.hideDialog = function(){
    this._editor.modal('hide');
};

TextPropertyEditor.prototype.startOpeningEditor = function(){
    var me = this;
    $.ajax({
        type: 'GET',
        dataType: 'json',
        cache: false,
        url: me.getWidgetData()['url'],
        data: me.getWidgetData(),
        success: function(data){
            if (data['success']) {
                me.makeEditor();
                me.setText($.trim(data['text']));
                me.openEditor();
            } else {
                showMessage(me.getElement(), data['message']);
            }
        }
    });
};

TextPropertyEditor.prototype.saveData = function(){
    var data = this.getWidgetData();
    data['text'] = this.getText();
    var me = this;
    $.ajax({
        type: 'POST',
        dataType: 'json',
        cache: false,
        url: me.getWidgetData()['url'],
        data: data,
        success: function(data) {
            if (data['success']) {
                me.showAlert(gettext('saved'));
                setTimeout(function(){
                    me.clearMessages();
                    me.hideDialog();
                }, 1000);
            } else {
                me.showError(data['message']);
            }
        }
    });
};

TextPropertyEditor.prototype.decorate = function(element){
    this._element = element;
    var me = this;
    setupButtonEventHandlers(element, function(){ me.startOpeningEditor() });
};

/**
 * A button on which user can click
 * and become added to some group (followers, group members, etc.)
 * or toggle some state on/off
 * The button has four states on-prompt, off-prompt, on-state and off-state
 * on-prompt is activated on mouseover, when user is not part of group
 * off-prompt - on mouseover, when user is part of group
 * on-state - when user is part of group and mouse is not over the button
 * off-state - same as above, but when user is not part of the group
 */
var TwoStateToggle = function(){
    SimpleControl.call(this);
    this._state = null;
    this._state_messages = {};
    this._states = [
        'on-state',
        'off-state',
        'on-prompt',
        'off-prompt'
    ];
    this._handler = this.getDefaultHandler();
    this._post_data = {};
    this.toggleUrl = '';//public property
};
inherits(TwoStateToggle, SimpleControl);

TwoStateToggle.prototype.setPostData = function(data){
    this._post_data = data;
};

TwoStateToggle.prototype.getPostData = function(){
    return this._post_data;
};

TwoStateToggle.prototype.resetStyles = function(){
    var element = this._element;
    var states = this._states;
    $.each(states, function(idx, state){
        element.removeClass(state);
    });
    this._element.html('');
};

TwoStateToggle.prototype.isOn = function(){
    return this._element.hasClass('on');
};

TwoStateToggle.prototype.getDefaultHandler = function(){
    var me = this;
    return function(){
        var data = me.getPostData();
        data['disable'] = me.isOn();
        $.ajax({
            type: 'POST',
            dataType: 'json',
            cache: false,
            url: me.toggleUrl,
            data: data,
            success: function(data) {
                if (data['success']) {
                    if ( data['is_enabled'] ) {
                        me.setState('on-state');
                    } else {
                        me.setState('off-state');
                    }
                } else {
                    showMessage(me.getElement(), data['message']);
                }
            }
        });
    };
};

TwoStateToggle.prototype.isCheckBox = function(){
    var element = this._element;
    return element.attr('type') === 'checkbox';
};

TwoStateToggle.prototype.setState = function(state){
    var element = this._element;
    this._state = state;
    if (element) {
        this.resetStyles();
        element.addClass(state);
        if (state === 'on-state') {
            element.addClass('on');
        } else if (state === 'off-state') {
            element.removeClass('on');
        }
        if ( this.isCheckBox() ) {
            if (state === 'on-state') {
                element.attr('checked', true);
            } else if (state === 'off-state') {
                element.attr('checked', false);
            }
        } else {
            this._element.html(this._state_messages[state]);
        }
    }
};

TwoStateToggle.prototype.decorate = function(element){
    this._element = element;
    //read messages for all states
    var messages = {};
    messages['on-state'] =
        element.attr('data-on-state-text') || gettext('enabled');
    messages['off-state'] = 
        element.attr('data-off-state-text') || gettext('disabled');
    messages['on-prompt'] =
        element.attr('data-on-prompt-text') || messages['on-state'];
    messages['off-prompt'] = 
        element.attr('data-off-prompt-text') || messages['off-state'];
    this._state_messages = messages;

    this.toggleUrl = element.attr('data-toggle-url');

    //detect state and save it
    if (this.isCheckBox()) {
        this._state = element.attr('checked') ? 'state-on' : 'state-off';
    } else {
        var text = $.trim(element.html());
        for (var i = 0; i < this._states.length; i++){
            var state = this._states[i];
            if (text === messages[state]){
                this._state = state;
                break;
            }
        }
    }

    //set mouseover handler
    var me = this;
    element.mouseover(function(){
        var is_on = me.isOn();
        if (is_on){
            me.setState('off-prompt');
        } else {
            me.setState('on-prompt');
        }
        element.css('background-color', 'red');
        return false;
    });
    element.mouseout(function(){
        var is_on = me.isOn();
        if (is_on){
            me.setState('on-state');
        } else {
            me.setState('off-state');
        }
        element.css('background-color', 'white');
        return false;
    });

    setupButtonEventHandlers(element, this.getHandler());
};

/**
 * A list of items from where one can be selected
 */
var SelectBox = function(){
    WrappedElement.call(this);
    this._items = [];
};
inherits(SelectBox, WrappedElement);

SelectBox.prototype.removeItem = function(id){
    var item = this.getItem(id);
    item.fadeOut();
    item.remove();
};

SelectBox.prototype.getItem = function(id){
    return $(this._element.find('li[data-item-id="' + id + '"]'));
};

SelectBox.prototype.addItem = function(id, title, details){
    /*this._items.push({
        id: id,
        title: title,
        details: details
    });*/
    if (this._element){
        var li = this.getItem(id);
        var new_li = false;
        if (li.length !== 1){
            li = this.makeElement('li');
            new_li = true;
        }
        li.attr('data-item-id', id)
            .attr('data-original-title', details)
            .html(title);
        if (new_li){
            this._element.append(li);
        }
        this.selectItem($(li));
        var me = this;
        setupButtonEventHandlers(
            $(li),
            function(){
                me.selectItem($(li));
            }
        );
    }
};

SelectBox.prototype.getSelectedItemData = function(){
    var item = $(this._element.find('li.selected')[0]);
    return {
        id: item.attr('data-item-id'),
        title: item.html(),
        details: item.attr('data-original-title')
    };
};

SelectBox.prototype.selectItem = function(item){
    this._element.find('li').removeClass('selected');
    item.addClass('selected');
};

SelectBox.prototype.decorate = function(element){
    this._element = element;
    var me = this;
    this._element.find('li').each(function(itx, item){
        setupButtonEventHandlers(
            $(item),
            function(){
                me.selectItem($(item));
            }
        );
    });
};

var Tag = function(){
    SimpleControl.call(this);
    this._deletable = false;
    this._delete_handler = null;
    this._delete_icon_title = null;
    this._tag_title = null;
    this._name = null;
    this._url_params = null;
    this._inner_html_tag = 'a';
    this._html_tag = 'li';
}
inherits(Tag, SimpleControl);

Tag.prototype.setName = function(name){
    this._name = name;
};

Tag.prototype.getName = function(){
    return this._name;
};

Tag.prototype.setHtmlTag = function(html_tag){
    this._html_tag = html_tag;
};

Tag.prototype.setDeletable = function(is_deletable){
    this._deletable = is_deletable;
};

Tag.prototype.setLinkable = function(is_linkable){
    if (is_linkable === true){
        this._inner_html_tag = 'a';
    } else {
        this._inner_html_tag = 'span';
    }
};

Tag.prototype.isLinkable = function(){
    return (this._inner_html_tag === 'a');
};

Tag.prototype.isDeletable = function(){
    return this._deletable;
};

Tag.prototype.isWildcard = function(){
    return (this.getName().substr(-1) === '*');
};

Tag.prototype.setUrlParams = function(url_params){
    this._url_params = url_params;
};

Tag.prototype.setHandlerInternal = function(){
    setupButtonEventHandlers(this._element.find('.tag'), this._handler);
};

/* delete handler will be specific to the task */
Tag.prototype.setDeleteHandler = function(delete_handler){
    this._delete_handler = delete_handler;
    if (this.hasElement() && this.isDeletable()){
        this._delete_icon.setHandler(delete_handler);
    }
};

Tag.prototype.getDeleteHandler = function(){
    return this._delete_handler;
};

Tag.prototype.setDeleteIconTitle = function(title){
    this._delete_icon_title = title;
};

Tag.prototype.decorate = function(element){
    this._element = element;
    var del = element.find('.delete-icon');
    if (del.length === 1){
        this.setDeletable(true);
        this._delete_icon = new DeleteIcon();
        if (this._delete_icon_title != null){
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        //do not set the delete handler here
        this._delete_icon.decorate(del);
    }
    this._inner_element = this._element.find('.tag');
    this._name = this.decodeTagName(
        $.trim(this._inner_element.attr('data-tag-name'))
    );
    if (this._title !== null){
        this._inner_element.attr('title', this._title);
    }
    if (this._handler !== null){
        this.setHandlerInternal();
    }
};

Tag.prototype.getDisplayTagName = function(){
    //replaces the trailing * symbol with the unicode asterisk
    return this._name.replace(/\*$/, '&#10045;');
};

Tag.prototype.decodeTagName = function(encoded_name){
    return encoded_name.replace('\u273d', '*');
};

Tag.prototype.createDom = function(){
    this._element = this.makeElement(this._html_tag);
    //render the outer element
    if (this._deletable){
        this._element.addClass('deletable-tag');
    }
    this._element.addClass('tag-left');

    //render the inner element
    this._inner_element = this.makeElement(this._inner_html_tag);
    if (this.isLinkable()){
        var url = askbot['urls']['questions'];
        var flag = false
        var author = ''
        if (this._url_params){
            url += QSutils.add_search_tag(this._url_params, this.getName());
        }
        this._inner_element.attr('href', url);
    }
    this._inner_element.addClass('tag tag-right');
    this._inner_element.attr('rel', 'tag');
    if (this._title === null){
        this.setTitle(
            interpolate(gettext("see questions tagged '%s'"), [this.getName()])
        );
    }
    this._inner_element.attr('title', this._title);
    this._inner_element.html(this.getDisplayTagName());

    this._element.append(this._inner_element);

    if (!this.isLinkable() && this._handler !== null){
        this.setHandlerInternal();
    }

    if (this._deletable){
        this._delete_icon = new DeleteIcon();
        this._delete_icon.setHandler(this.getDeleteHandler());
        if (this._delete_icon_title !== null){
            this._delete_icon.setTitle(this._delete_icon_title);
        }
        var del_icon_elem = this._delete_icon.getElement();
        del_icon_elem.text('x'); // HACK by Tomasz
        this._element.append(del_icon_elem);
    }
};

//Search Engine Keyword Highlight with Javascript
//http://scott.yang.id.au/code/se-hilite/
Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["local","q"],["cnprog\\.","q"],["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function(d){var g=null;var e=new RegExp("");for(var c=0;c<Hilite.search_engines.length;c++){var f=Hilite.search_engines[c];e.compile("^http://(www\\.)?"+f[0],"i");var b=d.match(e);if(b){var a;if(isNaN(f[1])){a=Hilite.decodeReferrerQS(d,f[1])}else{a=b[f[1]+1]}if(a){a=decodeURIComponent(a);if(f.length>2&&f[2]){a=decodeURIComponent(a)}a=a.replace(/\'|"/g,"");a=a.split(/[\s,\+\.]+/);return a}break}}return null};Hilite.decodeReferrerQS=function(f,d){var b=f.indexOf("?");var c;if(b>=0){var a=new String(f.substring(b+1));b=0;c=0;while((b>=0)&&((c=a.indexOf("=",b))>=0)){var e,g;e=a.substring(b,c);b=a.indexOf("&",c)+1;if(e==d){if(b<=0){return a.substring(c+1)}else{return a.substring(c+1,b-1)}}else{if(b<=0){return null}}}}return null};Hilite.hiliteElement=function(f,e){if(!e||f.childNodes.length==0){return}var c=new Array();for(var b=0;b<e.length;b++){e[b]=e[b].toLowerCase();if(Hilite.exact){c.push("\\b"+e[b]+"\\b")}else{c.push(e[b])}}c=new RegExp(c.join("|"),"i");var a={};for(var b=0;b<e.length;b++){if(Hilite.style_name_suffix){a[e[b]]=Hilite.style_name+(b+1)}else{a[e[b]]=Hilite.style_name}}var d=function(m){var j=c.exec(m.data);if(j){var n=j[0];var i="";var h=m.splitText(j.index);var g=h.splitText(n.length);var l=m.ownerDocument.createElement("SPAN");m.parentNode.replaceChild(l,h);l.className=a[n.toLowerCase()];l.appendChild(h);return l}else{return m}};Hilite.walkElements(f.childNodes[0],1,d)};Hilite.hilite=function(){var a=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var b=null;a=Hilite.decodeReferrer(a);if(a&&((Hilite.elementid&&(b=document.getElementById(Hilite.elementid)))||(b=document.body))){Hilite.hiliteElement(b,a)}};Hilite.walkElements=function(d,f,e){var a=/^(script|style|textarea)/i;var c=0;while(d&&f>0){c++;if(c>=Hilite.max_nodes){var b=function(){Hilite.walkElements(d,f,e)};setTimeout(b,50);return}if(d.nodeType==1){if(!a.test(d.tagName)&&d.childNodes.length>0){d=d.childNodes[0];f++;continue}}else{if(d.nodeType==3){d=e(d)}}if(d.nextSibling){d=d.nextSibling}else{while(f>0){d=d.parentNode;f--;if(d.nextSibling){d=d.nextSibling;break}}}}};if(Hilite.onload){if(window.attachEvent){window.attachEvent("onload",Hilite.hilite)}else{if(window.addEventListener){window.addEventListener("load",Hilite.hilite,false)}else{var __onload=window.onload;window.onload=function(){Hilite.hilite();__onload()}}}};
/* json2.js by D. Crockford */
if(!this.JSON){this.JSON={}}(function(){function f(n){return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(key){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf()}}var cx=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,escapable=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,gap,indent,meta={"\b":"\\b","\t":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?'"'+string.replace(escapable,function(a){var c=meta[a];return typeof c==="string"?c:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+string+'"'}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function"){value=value.toJSON(key)}if(typeof rep==="function"){value=rep.call(holder,key,value)}switch(typeof value){case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value){return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]"){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object"){length=rep.length;for(i=0;i<length;i+=1){k=rep[i];if(typeof k==="string"){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value){if(Object.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\n"+gap+partial.join(",\n"+gap)+"\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function"){JSON.stringify=function(value,replacer,space){var i;gap="";indent="";if(typeof space==="number"){for(i=0;i<space;i+=1){indent+=" "}}else{if(typeof space==="string"){indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function"){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==="object"){for(k in value){if(Object.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\],:{}\s]*$/.test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());
//jquery fieldselection
(function(){var a={getSelection:function(){var b=this.jquery?this[0]:this;return(("selectionStart" in b&&function(){var c=b.selectionEnd-b.selectionStart;return{start:b.selectionStart,end:b.selectionEnd,length:c,text:b.value.substr(b.selectionStart,c)}})||(document.selection&&function(){b.focus();var d=document.selection.createRange();if(d==null){return{start:0,end:b.value.length,length:0}}var c=b.createTextRange();var e=c.duplicate();c.moveToBookmark(d.getBookmark());e.setEndPoint("EndToStart",c);return{start:e.text.length,end:e.text.length+d.text.length,length:d.text.length,text:d.text}})||function(){return{start:0,end:b.value.length,length:0}})()},replaceSelection:function(){var b=this.jquery?this[0]:this;var c=arguments[0]||"";return(("selectionStart" in b&&function(){b.value=b.value.substr(0,b.selectionStart)+c+b.value.substr(b.selectionEnd,b.value.length);return this})||(document.selection&&function(){b.focus();document.selection.createRange().text=c;return this})||function(){b.value+=c;return this})()}};jQuery.each(a,function(b){jQuery.fn[b]=this})})();

(function($){function isRGBACapable(){var $script=$("script:first"),color=$script.css("color"),result=false;if(/^rgba/.test(color)){result=true}else{try{result=(color!=$script.css("color","rgba(0, 0, 0, 0.5)").css("color"));$script.css("color",color)}catch(e){}}return result}$.extend(true,$,{support:{rgba:isRGBACapable()}});var properties=["color","backgroundColor","borderBottomColor","borderLeftColor","borderRightColor","borderTopColor","outlineColor"];$.each(properties,function(i,property){$.fx.step[property]=function(fx){if(!fx.init){fx.begin=parseColor($(fx.elem).css(property));fx.end=parseColor(fx.end);fx.init=true}fx.elem.style[property]=calculateColor(fx.begin,fx.end,fx.pos)}});$.fx.step.borderColor=function(fx){if(!fx.init){fx.end=parseColor(fx.end)}var borders=properties.slice(2,6);$.each(borders,function(i,property){if(!fx.init){fx[property]={begin:parseColor($(fx.elem).css(property))}}fx.elem.style[property]=calculateColor(fx[property].begin,fx.end,fx.pos)});fx.init=true};function calculateColor(begin,end,pos){var color="rgb"+($.support.rgba?"a":"")+"("+parseInt((begin[0]+pos*(end[0]-begin[0])),10)+","+parseInt((begin[1]+pos*(end[1]-begin[1])),10)+","+parseInt((begin[2]+pos*(end[2]-begin[2])),10);if($.support.rgba){color+=","+(begin&&end?parseFloat(begin[3]+pos*(end[3]-begin[3])):1)}color+=")";return color}function parseColor(color){var match,triplet;if(match=/#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})/.exec(color)){triplet=[parseInt(match[1],16),parseInt(match[2],16),parseInt(match[3],16),1]}else{if(match=/#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])/.exec(color)){triplet=[parseInt(match[1],16)*17,parseInt(match[2],16)*17,parseInt(match[3],16)*17,1]}else{if(match=/rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(color)){triplet=[parseInt(match[1]),parseInt(match[2]),parseInt(match[3]),1]}else{if(match=/rgba\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9\.]*)\s*\)/.exec(color)){triplet=[parseInt(match[1],10),parseInt(match[2],10),parseInt(match[3],10),parseFloat(match[4])]}else{if(color=="transparent"){triplet=[0,0,0,0]}}}}}return triplet}})(jQuery);
