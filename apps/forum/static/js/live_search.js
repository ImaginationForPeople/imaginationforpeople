var TagWarningBox = function(){
    WrappedElement.call(this);
    this._tags = [];
};
inherits(TagWarningBox, WrappedElement);

TagWarningBox.prototype.createDom = function(){
    this._element = this.makeElement('div');
    this._element
        .css('display', 'block')
        .css('margin', '0 0 13px 2px');
    this._element.addClass('non-existing-tags');
    this._warning = this.makeElement('p');
    this._element.append(this._warning);
    this._tag_container = this.makeElement('ul');
    this._tag_container.addClass('tags');
    this._element.append(this._tag_container);
    this._element.append($('<div class="clearfix"></div>'));
    this._element.hide();
};

TagWarningBox.prototype.clear = function(){
    this._tags = [];
    if (this._tag_container){
        this._tag_container.empty();
    }
    this._warning.hide();
    this._element.hide();
};

TagWarningBox.prototype.addTag = function(tag_name){
   var tag = new Tag();
   tag.setName(tag_name);
   tag.setLinkable(false);
   tag.setDeletable(false);
   var elem = this.getElement();
   this._tag_container.append(tag.getElement());
   this._tag_container.css('display', 'block');
   this._tags.push(tag);
   elem.show();
};

TagWarningBox.prototype.showWarning = function(){
    this._warning.html(
        ngettext(
            'Sorry, this tag does not exist',
            'Sorry, these tags do not exist',
            this._tags.length
        )
    );
    this._warning.show();
};

var liveSearch = function(query_string) {
    var query = $('input#keywords');
    var query_val = function () {return $.trim(query.val());};
    var prev_text = query_val();
    var running = false;
    var q_list_sel = 'question-list';//id of question listing div
    var search_url = askbot['urls']['questions'];
    var x_button = $('input[name=reset_query]');
    var tag_warning_box = new TagWarningBox();

    //the tag search input is optional in askbot
    $('#ab-tag-search').parent().before(
        tag_warning_box.getElement()
    );

    var run_tag_search = function(){
        var search_tags = $('#ab-tag-search').val().split(/\s+/);
        if (search_tags.length === 0) {
            return;
        }
        /** @todo: the questions/ might need translation... */
        query_string = '/questions/scope:all/sort:activity-desc/page:1/'
        $.each(search_tags, function(idx, tag) {
            query_string = QSutils.add_search_tag(query_string, search_tags);
        });
        var url = search_url + query_string;
        $.ajax({
            url: url,
            dataType: 'json',
            success: function(data, text_status, xhr){
                render_result(data, text_status, xhr);
                $('#ab-tag-search').val('');
            },
        });
        updateHistory(url);
    };

    var activate_tag_search_input = function(){
        //the autocomplete is set up in tag_selector.js
        var button = $('#ab-tag-search-add');
        if (button.length === 0){//may be absent
            return;
        }
        var ac = new AutoCompleter({
            url: askbot['urls']['get_tag_list'],
            preloadData: true,
            minChars: 1,
            useCache: true,
            matchInside: true,
            maxCacheLength: 100,
            maxItemsToShow: 20,
            onItemSelect: run_tag_search,
            delay: 10
        });
        ac.decorate($('#ab-tag-search'));
        setupButtonEventHandlers(button, run_tag_search);
        //var tag_search_input = $('#ab-tag-search');
        //tag_search_input.keydown(
        //    makeKeyHandler(13, run_tag_search)
        //);
    };

    var render_tag_warning = function(tag_list){
        if ( !tag_list ) {
            return;
        }
        tag_warning_box.clear();
        $.each(tag_list, function(idx, tag_name){
            tag_warning_box.addTag(tag_name);
        });
        tag_warning_box.showWarning();
    };

    var refresh_x_button = function(){
        if(query_val().length > 0){
            if (query.hasClass('searchInput')){
                query.attr('class', 'searchInputCancelable');
                x_button.show();
            }
        } else {
            x_button.hide();
            query.attr('class', 'searchInput');
        }
    };

    var restart_query = function() {
        sortMethod = 'activity-desc';
        query.val('');
        refresh_x_button();
        send_query();
    };

    var eval_query = function(){
        cur_query = query_val();
        if (cur_query !== prev_text && running === false){
            if (cur_query.length >= minSearchWordLength){
                send_query(cur_query);
            } else if (cur_query.length === 0){
                restart_query();
            }
        }
    };

    var update_query_string = function(query_text){
        if(query_text === undefined) { // handle missing parameter
            query_text = query_val();
        }
        query_string = QSutils.patch_query_string(
                query_string,
                'query:' + encodeURIComponent(query_text),
                query_text === ''   // remove if empty
        );
        return query_text;
    };

    var send_query = function(query_text){
        running = true;
        if(!prev_text && query_text && showSortByRelevance) {
            // If there was no query but there is some query now - and we support relevance search - then switch to it */
            query_string = QSutils.patch_query_string(query_string, 'sort:relevance-desc');
        }
        prev_text = update_query_string(query_text);
        query_string = QSutils.patch_query_string(query_string, 'page:1'); /* if something has changed, then reset the page no. */
        var url = search_url + query_string;
        $.ajax({
            url: url,
            dataType: 'json',
            success: render_result,
            complete: function(){
                running = false;
                eval_query();
            },
            cache: false
        });
        updateHistory(url);
    };

    var updateHistory = function(url) {
        var context = { state:1, rand:Math.random() };
        History.pushState( context, "Questions", url );
        setTimeout(function (){
            /* HACK: For some weird reson, sometimes something overrides the above pushState so we re-aplly it
                     This might be caused by some other JS plugin.
                     The delay of 10msec allows the other plugin to override the URL.
            */
            History.replaceState( context, "Questions", url );
        }, 10);
    };

    /* *********************************** */

    var render_related_tags = function(tags, query_string){
        if (tags.length === 0) return;

        var html_list = [];
        for (var i=0; i<tags.length; i++){
            var tag = new Tag();
            tag.setName(tags[i]['name']);
            tag.setDeletable(false);
            tag.setLinkable(true);
            tag.setUrlParams(query_string);

            html_list.push(tag.getElement().outerHTML());
            html_list.push('<span class="tag-number">&#215; ');
            html_list.push(tags[i]['used_count']);
            html_list.push('</span>');
            html_list.push('<br />');
        }
        $('#related-tags').html(html_list.join(''));
    };

    var render_search_tags = function(tags, query_string){
        var search_tags = $('#searchTags');
        search_tags.empty();
        if (tags.length === 0){
            $('#listSearchTags').hide();
            $('#search-tips').hide();//wrong - if there are search users
        } else {
            $('#listSearchTags').show();
            $('#search-tips').show();
            $.each(tags, function(idx, tag_name){
                var tag = new Tag();
                tag.setName(tag_name);
                tag.setLinkable(false);
                tag.setDeletable(true);
                tag.setDeleteHandler(
                    function(){
                        remove_search_tag(tag_name, query_string);
                    }
                );
                search_tags.append(tag.getElement());
            });
        }
    };

    var create_relevance_tab = function(query_string){
        relevance_tab = $('<a></a>');
        href = search_url + QSutils.patch_query_string(query_string, 'sort:relevance-desc');
        relevance_tab.attr('href', href);
        relevance_tab.attr('id', 'by_relevance');
        relevance_tab.html('<span>' + sortButtonData['relevance']['label'] + '</span>');
        return relevance_tab;
    };

    /* *************************************** */

    var remove_search_tag = function(tag){
        query_string = QSutils.remove_search_tag(query_string, tag);
        send_query();
    };

    var set_active_sort_tab = function(sort_method, query_string){
        var tabs = $('#sort_tabs > a');
        tabs.attr('class', 'off');
        tabs.each(function(index, element){
            var tab = $(element);
            if ( tab.attr('id') ) {
                var tab_name = tab.attr('id').replace(/^by_/,'');
                if (tab_name in sortButtonData){
                    href = search_url + QSutils.patch_query_string(
                                            query_string,
                                            'sort:' + tab_name + '-desc'
                                        );
                    tab.attr('href', href);
                    tab.attr('title', sortButtonData[tab_name]['desc_tooltip']);
                    tab.html(sortButtonData[tab_name]['label']);
                }
            }
        });
        var bits = sort_method.split('-', 2);
        var name = bits[0];
        var sense = bits[1];//sense of sort
        var antisense = (sense == 'asc' ? 'desc':'asc');
        var arrow = (sense == 'asc' ? ' &#9650;':' &#9660;');
        var active_tab = $('#by_' + name);
        active_tab.attr('class', 'on');
        active_tab.attr('title', sortButtonData[name][antisense + '_tooltip']);
        active_tab.html(sortButtonData[name]['label'] + arrow);
    };

    var render_relevance_sort_tab = function(query_string){
        if (showSortByRelevance === false){
            return;
        }
        var relevance_tab = $('#by_relevance');
        if (prev_text && prev_text.length > 0){
            if (relevance_tab.length == 0){
                relevance_tab = create_relevance_tab(query_string);
                $('#sort_tabs>span').after(relevance_tab);
            }
        }
        else {
            if (relevance_tab.length > 0){
                relevance_tab.remove();
            }
        }
    };

    var render_result = function(data, text_status, xhr){
        if (data['questions'].length > 0){
            $('#pager').toggle(data['paginator'] !== '').html(data['paginator']);
            $('#questionCount').html(data['question_counter']);
            render_search_tags(data['query_data']['tags'], data['query_string']);
            if(data['faces'].length > 0) {
                $('#contrib-users > a').remove();
                $('#contrib-users').append(data['faces'].join(''));
            }
            render_related_tags(data['related_tags'], data['query_string']);
            render_relevance_sort_tab(data['query_string']);
            render_tag_warning(data['non_existing_tags']);
            set_active_sort_tab(data['query_data']['sort_order'], data['query_string']);
            if(data['feed_url']){
                // Change RSS URL
                $("#ContentLeft a.rss:first").attr("href", data['feed_url']);
            }

            // Patch scope selectors
            $('#scopeWrapper > a.scope-selector').each(function(index) {
                var old_qs = $(this).attr('href').replace(search_url, '');
                var scope = QSutils.get_query_string_selector_value(old_qs, 'scope');
                qs = QSutils.patch_query_string(data['query_string'], 'scope:' + scope);
                $(this).attr('href', search_url + qs);
            });

            // Patch "Ask your question"
            var askButton = $('#askButton');
            var askHrefBase = askButton.attr('href').split('?')[0];
            askButton.attr('href', askHrefBase + data['query_data']['ask_query_string']); /* INFO: ask_query_string should already be URL-encoded! */

            query.focus();

            var old_list = $('#' + q_list_sel);
            var new_list = $('<div></div>').hide().html(data['questions']);
            new_list.find('.timeago').timeago();
            old_list.stop(true).after(new_list).fadeOut(200, function() {
                //show new div with a fadeIn effect
                old_list.remove();
                new_list.attr('id', q_list_sel);
                new_list.fadeIn(400);            
            });
        }
    };

    /* *********************************** */

    // Wire search tags
    var search_tags = $('#searchTags .tag-left');
    $.each(search_tags, function(idx, element){
        var tag = new Tag();
        tag.decorate($(element));
        //todo: setDeleteHandler and setHandler
        //must work after decorate & must have getName
        tag.setDeleteHandler(
                function(){
                    remove_search_tag(tag.getName(), query_string);
                }
        );
    });

    // Wire X button
    x_button.click(function () {
        restart_query(); /* wrapped in closure because it's not yet defined at this point */
    });
    refresh_x_button();

    // Wire query box
    var main_page_eval_handle;
    query.keyup(function(e){
        refresh_x_button();
        if (running === false){
            clearTimeout(main_page_eval_handle);
            main_page_eval_handle = setTimeout(eval_query, 400);
        }
    });

    activate_tag_search_input();

    $("form#searchForm").submit(function(event) {
        // if user clicks the button the s(h)e probably wants page reload,
        // so provide that experience but first update the query string
        event.preventDefault();
        update_query_string();
        window.location.href = search_url + query_string;
    });

    /* *********************************** */

    // Hook for tag_selector.js
    liveSearch.refresh = function () {
        send_query();
    };
};
