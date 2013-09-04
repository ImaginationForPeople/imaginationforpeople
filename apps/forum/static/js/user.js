var setup_inbox = function(){

    var getSelected = function(){

        var id_list = new Array();
        var elements = $('#responses input:checked').parent();

        elements.each(function(index, element){
            var id = $(element).attr('id').replace(/^re_/,'');
            id_list.push(id);
        });

        if (id_list.length === 0){
            alert(gettext('Please select at least one item'));
        }

        return {id_list: id_list, elements: elements};
    };

    var submit = function(id_list, elements, action_type){
        if (action_type == 'delete' || action_type == 'mark_new' || action_type == 'mark_seen' || action_type == 'remove_flag' || action_type == 'delete_post'){
            $.ajax({
                type: 'POST',
                cache: false,
                dataType: 'json',
                data: JSON.stringify({memo_list: id_list, action_type: action_type}),
                url: askbot['urls']['manageInbox'],
                success: function(response_data){
                    if (response_data['success'] == true){
                        if (action_type == 'delete' || action_type == 'remove_flag' || action_type == 'delete_post'){
                            elements.remove();
                        }
                        else if (action_type == 'mark_new'){
                            elements.addClass('highlight');
                            elements.addClass('new');
                            elements.removeClass('seen');
                        }
                        else if (action_type == 'mark_seen'){
                            elements.removeClass('highlight');
                            elements.addClass('seen');
                            elements.removeClass('new');
                        }
                    }
                    else {
                        showMessage($('#responses'), response_data['message']);
                    }
                }
            });
        }
    };

    var startAction = function(action_type){
        var data = getSelected();
        if (data['id_list'].length === 0){
            return;
        }
        if (action_type == 'delete'){
            msg = ngettext('Delete this notification?',
					'Delete these notifications?', data['id_list'].length);
            if (confirm(msg) === false){
                return;
            }
        }
        if (action_type == 'close'){
            msg = ngettext('Close this entry?',
                    'Close these entries?', data['id_list'].length);
            if (confirm(msg) === false){
                return;
            }
        }
        if (action_type == 'remove_flag'){
            msg = ngettext(
                    'Remove all flags and approve this entry?',
                    'Remove all flags and approve these entries?',
                    data['id_list'].length
                );
            if (confirm(msg) === false){
                return;
            }
        }
        submit(data['id_list'], data['elements'], action_type);
    };
    setupButtonEventHandlers($('#re_mark_seen'), function(){startAction('mark_seen')});
    setupButtonEventHandlers($('#re_mark_new'), function(){startAction('mark_new')});
    setupButtonEventHandlers($('#re_dismiss'), function(){startAction('delete')});
    setupButtonEventHandlers($('#re_remove_flag'), function(){startAction('remove_flag')});
    //setupButtonEventHandlers($('#re_close'), function(){startAction('close')});
    setupButtonEventHandlers(
                    $('#sel_all'),
                    function(){
                        setCheckBoxesIn('#responses .new', true);
                        setCheckBoxesIn('#responses .seen', true);
                    }
    );
    setupButtonEventHandlers(
                    $('#sel_seen'),
                    function(){
                        setCheckBoxesIn('#responses .seen', true);
                    }
    );
    setupButtonEventHandlers(
                    $('#sel_new'),
                    function(){
                        setCheckBoxesIn('#responses .new', true);
                    }
    );
    setupButtonEventHandlers(
                    $('#sel_none'),
                    function(){
                        setCheckBoxesIn('#responses .new', false);
                        setCheckBoxesIn('#responses .seen', false);
                    }
    );

    var reject_post_dialog = new RejectPostDialog();
    reject_post_dialog.decorate($('#reject-edit-modal'));
    setupButtonEventHandlers(
        $('#re_delete_post'),
        function(){
            var data = getSelected();
            if (data['id_list'].length === 0){
                return;
            }
            reject_post_dialog.setSelectedEditData(data);
            reject_post_dialog.show();
        }
    );
    //setupButtonEventHandlers($('.re_expand'),
    //                function(e){
    //                    e.preventDefault();
    //                    var re_snippet = $(this).find(".re_snippet:first")
    //                    var re_content = $(this).find(".re_content:first")
    //                    $(re_snippet).slideToggle();
    //                    $(re_content).slideToggle();
    //                }
    //);
};

var setup_badge_details_toggle = function(){
    $('.badge-context-toggle').each(function(idx, elem){
        var context_list = $(elem).parent().next('ul');
        if (context_list.children().length > 0){
            $(elem).addClass('active');
            var toggle_display = function(){
                if (context_list.css('display') == 'none'){
                    $('.badge-context-list').hide();
                    context_list.show();
                } else {
                    context_list.hide();
                }
            };
            $(elem).click(toggle_display);
        }
    });
};

/**
 * @constructor
 * manages post/edit reject reasons
 * in the post moderation view
 */
var RejectPostDialog = function(){
    WrappedElement.call(this);
    this._selected_edit_ids = null;
    this._selected_reason_id = null;
    this._state = null;//'select', 'preview', 'add-new'
};
inherits(RejectPostDialog, WrappedElement);

RejectPostDialog.prototype.setSelectedEditData = function(data){
    this._selected_edit_data = data;
};

RejectPostDialog.prototype.setState = function(state){
    this._state = state;
    this.clearErrors();
    if (this._element){
        this._selector.hide();
        this._adder.hide();
        this._previewer.hide();
        if (state === 'select'){
            this._selector.show();
        } else if (state === 'preview'){
            this._previewer.show();
        } else if (state === 'add-new'){
            this._adder.show();
        }
    }
};

RejectPostDialog.prototype.show = function(){
    $(this._element).modal('show');
};

RejectPostDialog.prototype.hide = function(){
    $(this._element).modal('hide');
};

RejectPostDialog.prototype.resetInputs = function(){
    if (this._title_input){
        this._title_input.reset();
    }
    if (this._details_input){
        this._details_input.reset();
    }
    var selected = this._element.find('.selected');
    selected.removeClass('selected');
};

RejectPostDialog.prototype.clearErrors = function(){
    var error = this._element.find('.alert');
    error.remove();
};

RejectPostDialog.prototype.makeAlertBox = function(errors){
    //construct the alert box
    var alert_box = new AlertBox();
    alert_box.setClass('alert-error');
    if (typeof errors === "string"){
        alert_box.setText(errors);
    } else if (errors.constructor === [].constructor){
        if (errors.length > 1){
            alert_box.setContent(
                '<div>' + 
                gettext('Looks there are some things to fix:') +
                '</div>'
            )
            var list = this.makeElement('ul');
            $.each(errors, function(idx, item){
                list.append('<li>' + item + '</li>');
            });
            alert_box.addContent(list);
        } else if (errors.length == 1){
            alert_box.setContent(errors[0]);
        } else if (errors.length == 0){
            return;
        }
    } else if ('html' in errors){
        alert_box.setContent(errors);
    } else {
        return;//don't know what to do
    }
    return alert_box;
};

RejectPostDialog.prototype.setAdderErrors = function(errors){
    //clear previous errors
    this.clearErrors();
    var alert_box = this.makeAlertBox(errors);
    this._element
        .find('#reject-edit-modal-add-new .modal-body')
        .prepend(alert_box.getElement());
};

RejectPostDialog.prototype.setSelectorErrors = function(errors){
    this.clearErrors();
    var alert_box = this.makeAlertBox(errors);
    this._element
        .find('#reject-edit-modal-select .modal-body')
        .prepend(alert_box.getElement());
};

RejectPostDialog.prototype.setErrors = function(errors){
    this.clearErrors();
    var alert_box = this.makeAlertBox(errors);
    var current_state = this._state;
    this._element
        .find('#reject-edit-modal-' + current_state + ' .modal-body')
        .prepend(alert_box.getElement());
};

RejectPostDialog.prototype.addSelectableReason = function(data){
    var id = data['reason_id'];
    var title = data['title'];
    var details = data['details'];
    this._select_box.addItem(id, title, details);
};

RejectPostDialog.prototype.startSavingReason = function(callback){

    var title_input = this._title_input;
    var details_input = this._details_input;

    var errors = [];
    if (title_input.isBlank()){
        errors.push(gettext('Please provide description.'));
    }
    if (details_input.isBlank()){
        errors.push(gettext('Please provide details.'));
    }

    if (errors.length > 0){
        this.setAdderErrors(errors);
        return;//just show errors and quit
    }

    var data = {
        title: title_input.getVal(),
        details: details_input.getVal()
    };
    if (this._selected_reason_id){
        data['reason_id'] = this._selected_reason_id;
    }

    var me = this;

    $.ajax({
        type: 'POST',
        dataType: 'json',
        cache: false,
        url: askbot['urls']['save_post_reject_reason'],
        data: data,
        success: function(data){
            if (data['success']){
                //show current reason data and focus on it
                if (callback){
                    callback(data);
                } else {
                    me.addSelectableReason(data);
                    me.setState('select');
                }
            } else {
                me.setAdderErrors(data['message']);
            }
        }
    });
};

RejectPostDialog.prototype.rejectPost = function(reason_id){
    var me = this;
    var memos = this._selected_edit_data['elements'];
    var memo_ids = this._selected_edit_data['id_list'];
    var data = {
        reject_reason_id: reason_id,
        memo_list: memo_ids,
        action_type: 'delete_post'
    }
    $.ajax({
        type: 'POST',
        dataType: 'json',
        cache: false,
        data: JSON.stringify(data),
        url: askbot['urls']['manageInbox'],
        success: function(data){
            if (data['success']){
                memos.remove();
                me.hide();
            } else {
                //only fatal errors here
                me.setErrors(data['message']);
            }
        }
    });
};

RejectPostDialog.prototype.setPreviewerData = function(data){
    this._selected_reason_id = data['id'];
    this._element.find('.selected-reason-title').html(data['title']);
    this._element.find('.selected-reason-details').html(data['details']);
};

RejectPostDialog.prototype.startEditingReason = function(){
    var title = this._element.find('.selected-reason-title').html();
    var details = this._element.find('.selected-reason-details').html();
    this._title_input.setVal(title);
    this._details_input.setVal(details);
    this.setState('add-new');
};

RejectPostDialog.prototype.resetSelectedReasonId = function(){
    this._selected_reason_id = null;
};

RejectPostDialog.prototype.getSelectedReasonId = function(){
    return this._selected_reason_id;
};

RejectPostDialog.prototype.startDeletingReason = function(){
    var select_box = this._select_box;
    var data = select_box.getSelectedItemData();
    var reason_id = data['id'];
    var me = this;
    if (data['id']){
        $.ajax({
            type: 'POST',
            dataType: 'json',
            cache: false,
            url: askbot['urls']['delete_post_reject_reason'],
            data: {reason_id: reason_id},
            success: function(data){
                if (data['success']){
                    select_box.removeItem(reason_id);
                } else {
                    me.setSelectorErrors(data['message']);
                }
            }
        });
    } else {
        me.setSelectorErrors(
            gettext('A reason must be selected to delete one.')
        )
    }
};

RejectPostDialog.prototype.decorate = function(element){
    this._element = element;
    //set default state according to the # of available reasons
    this._selector = $(element).find('#reject-edit-modal-select');
    this._adder = $(element).find('#reject-edit-modal-add-new');
    this._previewer = $(element).find('#reject-edit-modal-preview');
    if (this._selector.find('li').length > 0){
        this.setState('select');
        this.resetInputs();
    } else {
        this.setState('add-new');
        this.resetInputs();
    }

    //$(this._element).find('.dropdown-toggle').dropdown();

    var select_box = new SelectBox();
    select_box.decorate($(this._selector.find('.select-box')));
    this._select_box = select_box;

    //setup tipped-inputs
    var reject_title_input = $(this._element).find('input');
    var title_input = new TippedInput();
    title_input.decorate($(reject_title_input));
    this._title_input = title_input;
    
    var reject_details_input = $(this._element)
        .find('textarea.reject-reason-details');

    var details_input = new TippedInput();
    details_input.decorate($(reject_details_input));
    this._details_input = details_input;

    var me = this;
    setupButtonEventHandlers(
        element.find('.cancel, .modal-header .close'),
        function() {
            me.hide();
            me.clearErrors();
            me.resetInputs();
            me.resetSelectedReasonId();
            me.setState('select');
        }
    );

    setupButtonEventHandlers(
        $(this._element).find('.save-reason'),
        function(){ me.startSavingReason() }
    );

    setupButtonEventHandlers(
        $(this._element).find('.save-reason-and-reject'),
        function(){
            me.startSavingReason(
                function(data){
                    me.rejectPost(data['reason_id']);
                }
            );
        }
    );

    setupButtonEventHandlers(
        $(this._element).find('.reject'),
        function(){
            me.rejectPost(me.getSelectedReasonId());
        }
    );

    setupButtonEventHandlers(
        element.find('.select-other-reason'),
        function(){ 
            me.resetInputs();
            me.setState('select');
        }
    )

    setupButtonEventHandlers(
        element.find('.add-new-reason'),
        function(){ 
            me.resetSelectedReasonId();
            me.resetInputs();
            me.setState('add-new') 
        }
    );

    setupButtonEventHandlers(
        element.find('.select-this-reason'),
        function(){
            var data = select_box.getSelectedItemData();
            if (data['id']){
                me.setState('preview');
                me.setPreviewerData(data);
            } else {
                me.setSelectorErrors(
                    gettext('A reason must be selected to reject post.')
                )
            }
        }
    );

    setupButtonEventHandlers(
        element.find('.edit-reason'),
        function(){
            me.startEditingReason();
        }
    );

    setupButtonEventHandlers(
        element.find('.delete-this-reason'),
        function(){
            me.startDeletingReason();
        }
    )
};
