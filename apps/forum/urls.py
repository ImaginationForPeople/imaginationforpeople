"""
askbot askbot url configuraion file
"""
import os.path
from django.conf import settings
from django.conf.urls.defaults import url, patterns, include
from django.conf.urls.defaults import handler500, handler404
from django.contrib import admin
from askbot import views
from askbot.feed import RssLastestQuestionsFeed, RssIndividualQuestionFeed
from askbot.sitemap import QuestionsSitemap

admin.autodiscover()

if getattr(settings, "ASKBOT_TRANSLATE_URL", False):
    from django.utils.translation import ugettext as _
else:
    _ = lambda s:s

feeds = {
    'rss': RssLastestQuestionsFeed,
    'question':RssIndividualQuestionFeed
}

APP_PATH = os.path.dirname(__file__)
urlpatterns = patterns('',
    url(r'^$', views.readers.index, name='forum-index'),
    (r'^settings/', include('askbot.deps.livesettings.urls')),
    (r'^followit/', include('followit.urls')),
    (r'^cache/', include('keyedcache.urls')),

    url(r'^%s(?P<id>\d+)/%s$' % (_('answers/'), _('edit/')), views.writers.edit_answer, name='edit_answer'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('answers/'), _('revisions/')), views.readers.revisions, kwargs = {'post_type': 'answer'}, name='answer_revisions'),

    # BEGIN Questions (main page) urls. All this urls work both normally and through ajax

    url(
        # Note that all parameters, even if optional, are provided to the view. Non-present ones have None value.
        (r'^%s' % _('questions') +
            r'(%s)?' % r'/scope:(?P<scope>\w+)' +
            r'(%s)?' % r'/sort:(?P<sort>[\w\-]+)' +
            r'(%s)?' % r'/query:(?P<query>[^/]+)' +  # INFO: question string cannot contain slash (/), which is a section terminator
            r'(%s)?' % r'/tags:(?P<tags>[\w+.#,-]+)' + # Should match: const.TAG_CHARS + ','; TODO: Is `#` char decoded by the time URLs are processed ??
            r'(%s)?' % r'/author:(?P<author>\d+)' +
            r'(%s)?' % r'/page:(?P<page>\d+)' +
        r'/$'),

        views.readers.QuestionsView.as_view(), 
        name='questions'
    ),

    # END main page urls
    
    url(
        r'^api/get_questions/',
        views.commands.api_get_questions,
        name = 'api_get_questions'
    ),
    url(
        r'^get-users-info/',
        views.commands.get_users_info,
        name='get_users_info'
    ),
    url(
        r'^%s%s$' % (_('questions/'), _('ask/')), 
        views.writers.ask, 
        name='ask'
    ),
    url(
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('edit/')), 
        views.writers.edit_question, 
        name='edit_question'
    ),
    url(#this url is both regular and ajax
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('retag/')), 
        views.writers.retag_question, 
        name='retag_question'
    ),
    url(
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('close/')), 
        views.commands.close, 
        name='close'
    ),
    url(
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('reopen/')), 
        views.commands.reopen, 
        name='reopen'
    ),
    url(
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('answer/')), 
        views.writers.answer, 
        name='answer'
    ),
    url(#ajax only
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('vote/')), 
        views.commands.vote, 
        name='vote'
    ),
    url(
        r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('revisions/')), 
        views.readers.revisions, 
        kwargs = {'post_type': 'question'},
        name='question_revisions'
    ),
    url(
        r'^%s%s$' % (_('widgets/'), _('questions/')),
        views.readers.widget_questions, 
        name='widget_questions'
    ),
    url(#ajax only
        r'^comment/upvote/$',
        views.commands.upvote_comment,
        name = 'upvote_comment'
    ),
    url(#ajax only
        r'^post/delete/$',
        views.commands.delete_post,
        name = 'delete_post'
    ),
    url(#ajax only
        r'^post_comments/$',
        views.writers.post_comments, 
        name='post_comments'
    ),
    url(#ajax only
        r'^edit_comment/$',
        views.writers.edit_comment,
        name='edit_comment'
    ),
    url(#ajax only
        r'^comment/delete/$',
        views.writers.delete_comment, 
        name='delete_comment'
    ),
    url(#ajax only
        r'^comment/get_text/$',
        views.readers.get_comment, 
        name='get_comment'
    ),
    url(
        r'^%s$' % _('tags/'), 
        views.readers.tags, 
        name='tags'
    ),
    #todo: collapse these three urls and use an extra json data var
    url(#ajax only
        r'^%s%s$' % ('mark-tag/', 'interesting/'),
        views.commands.mark_tag,
        kwargs={'reason':'good','action':'add'},
        name='mark_interesting_tag'
    ),
    url(#ajax only
        r'^%s%s$' % ('mark-tag/', 'ignored/'),
        views.commands.mark_tag,
        kwargs={'reason':'bad','action':'add'},
        name='mark_ignored_tag'
    ),
    url(#ajax only
        r'^%s%s$' % ('mark-tag/', 'subscribed/'),
        views.commands.mark_tag,
        kwargs={'reason':'subscribed','action':'add'},
        name='mark_subscribed_tag'
    ),
    url(#ajax only
        r'^unmark-tag/',
        views.commands.mark_tag,
        kwargs={'action':'remove'},
        name='unmark_tag'
    ),
    url(#ajax only
        r'^set-tag-filter-strategy/',
        views.commands.set_tag_filter_strategy,
        name = 'set_tag_filter_strategy'
    ),
    url(
        r'^get-tags-by-wildcard/',
        views.commands.get_tags_by_wildcard,
        name = 'get_tags_by_wildcard'
    ),
    url(
        r'^get-tag-list/',
        views.commands.get_tag_list,
        name = 'get_tag_list'
    ),
    url(
        r'^load-tag-wiki-text/',
        views.commands.load_tag_wiki_text,
        name = 'load_tag_wiki_text'
    ),
    url(#ajax only
        r'^save-tag-wiki-text/',
        views.commands.save_tag_wiki_text,
        name = 'save_tag_wiki_text'
    ),
    url(#ajax only
        r'^save-group-logo-url/',
        views.commands.save_group_logo_url,
        name = 'save_group_logo_url'
    ),
    url(#ajax only
        r'^delete-group-logo/',
        views.commands.delete_group_logo,
        name = 'delete_group_logo'
    ),
    url(#ajax only
        r'^toggle-group-profile-property/',
        views.commands.toggle_group_profile_property,
        name = 'toggle_group_profile_property'
    ),
    url(#ajax only
        r'^edit-object-property-text/',
        views.commands.edit_object_property_text,
        name = 'edit_object_property_text'
    ),
    url(
        r'^get-groups-list/',
        views.commands.get_groups_list,
        name = 'get_groups_list'
    ),
    url(
        r'^swap-question-with-answer/',
        views.commands.swap_question_with_answer,
        name = 'swap_question_with_answer'
    ),
    url(
        r'^%s$' % _('subscribe-for-tags/'),
        views.commands.subscribe_for_tags,
        name = 'subscribe_for_tags'
    ),
    url(
        r'^%s$' % _('users/'),
        views.users.show_users, 
        name='users'
    ),
    url(
        r'^%s%s(?P<group_id>\d+)/(?P<group_slug>.*)/$' % (_('users/'), _('by-group/')),
        views.users.show_users, 
        kwargs = {'by_group': True},
        name = 'users_by_group'
    ),
    url(
        r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (
            _('users/'),
            _('subscriptions/'),
        ),
        views.users.user_profile,
        kwargs = {'tab_name': 'email_subscriptions'},
        name = 'user_subscriptions'
    ),
    url(
        r'^%s$' % _('groups/'),
        views.users.groups,
        name='groups'
    ),
    url(
        r'^%s$' % _('badges/'),
        views.meta.badges,
        name='badges'
    ),
    url(
        r'^%s(?P<id>\d+)//*' % _('badges/'),
        views.meta.badge,
        name='badge'
    ),
    url(#ajax only
        r'^manage-inbox/$',
        views.commands.manage_inbox,
        name='manage_inbox'
    ),
    url(#ajax only
        r'^save-post-reject-reason/$',
        views.commands.save_post_reject_reason,
        name='save_post_reject_reason'
    ),
    url(#ajax only
        r'^delete-post-reject-reason/$',
        views.commands.delete_post_reject_reason,
        name='delete_post_reject_reason'
    ),
    url(#ajax only
        r'^edit-group-membership/$',
        views.commands.edit_group_membership,
        name='edit_group_membership'
    ),
    url(#ajax only
        r'^join-or-leave-group/$',
        views.commands.join_or_leave_group,
        name = 'join_or_leave_group'
    ),
    url(#ajax only
        r'^rev/$',
        views.readers.get_revision, 
        name='get_revision'
    ),

    url(r'^questions/rss/$', RssLastestQuestionsFeed(), name="latest_questions_feed"),
    url(r'^question/(?P<question_id>\d+)/rss/$', RssIndividualQuestionFeed(), name="question_feed"),
    
    #upload url is ajax only
    url( r'^%s$' % _('upload/'), views.writers.upload, name='upload'),
    url(
        '^custom\.css$',
        views.meta.config_variable,
        kwargs = {
            'variable_name': 'CUSTOM_CSS',
            'mimetype': 'text/css'
        },
        name = 'custom_css'
    ),
    url(
        '^custom\.js$',
        views.meta.config_variable,
        kwargs = {
            'variable_name': 'CUSTOM_JS',
            'mimetype': 'text/javascript'
        },
        name = 'custom_js'
    ),
    url(r'^%s(?P<question_id>\d+)/' % _('question/'), views.readers.QuestionView.as_view(), name='question'),
)
