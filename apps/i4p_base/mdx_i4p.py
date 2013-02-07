from markdown.inlinepatterns import SimpleTagPattern

from markdown import Extension
from markdown.util import etree

from django.core.urlresolvers import reverse


class UserTagPattern(SimpleTagPattern):
    """
    Matches a user : @JohnDoe
    """
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\@([\w-]+)', 'a')
        
    def handleMatch(self, m):
        from django.contrib.auth.models import User
        el = etree.Element(self.tag)
        username = m.group(2)
        try:
            user = User.objects.get(username__iexact=username)
            el.text = u"@%s" % user.get_profile().get_full_name_or_username()
            el.attrib['href'] = user.get_profile().get_absolute_url()
        except:
            el.text = "Unknown user (%s)" % (username)

        return el

class ThemeTagPattern(SimpleTagPattern):
    """
    A pattern that matches a thematic page, such as #innovation
    """
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\#([\w-]+)', 'a')
        
    def handleMatch(self, m):
        el = etree.Element(self.tag)
        theme = m.group(2)
        try:
            el.text = u"#%s" % theme
            el.attrib['href'] = reverse('tags:tag-view', args=(theme,))
        except:
            el.text = "Unknown theme (%s)" % (theme)

        return el
        

class ProjectTagPattern(SimpleTagPattern):
    """
    Matches a project slug and its languages. Eg: |fr|project-slug
    """
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\|([A-z][A-z])\|([\w-]+)', 'a')
        
    def handleMatch(self, m):
        from apps.project_sheet.models import I4pProjectTranslation # Don't move this to the top, it will circular imports
        el = etree.Element(self.tag)
        language = m.group(2)
        slug = m.group(3)
        try:
            project_translation = I4pProjectTranslation.objects.get(language_code=language, slug=slug)
            el.text = u"|%s|%s" % (language, project_translation.title)
            el.attrib['href'] = project_translation.get_absolute_url()
        except:
            el.text = "Unknown project (%s, %s)" % (language, slug)

        return el

class GroupTagPattern(SimpleTagPattern):
    """
    A group pattern such as +group
    """
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\+([\w-]+)', 'a')
        
    def handleMatch(self, m):
        from apps.workgroup.models import WorkGroup # Don't move this to the top, it will circular imports
        el = etree.Element(self.tag)
        group_slug = m.group(2)
        try:
            group = WorkGroup.objects.get(slug=group_slug)
            el.text = u"+%s" % group.name
            el.attrib['href'] = group.get_absolute_url()
        except:
            el.text = "Unknown group (%s)" % (group_slug)

        return el
        
class ForumThreadTagPattern(SimpleTagPattern):
    """
    Matches a forum question : ?203
    """
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\?(\d+)', 'a')
        
    def handleMatch(self, m):
        from askbot.models.question import Thread
        el = etree.Element(self.tag)
        thread_id = m.group(2)
        try:
            thread = Thread.objects.get(id=thread_id)
            el.text = u"?%s - \"%s\"" % (thread_id,
                                        thread.title)
            el.attrib['href'] = thread.get_absolute_url()
        except:
            el.text = "Unknown forum thread (%s)" % (thread_id)

        return el

        
class I4pExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('grouppattern', GroupTagPattern(), '_begin')
        md.inlinePatterns.add('projectpattern', ProjectTagPattern(), '_begin')
        md.inlinePatterns.add('userpattern', UserTagPattern(), '_begin')
        md.inlinePatterns.add('themepattern', ThemeTagPattern(), '_begin')
        md.inlinePatterns.add('forumthreadpattern', ForumThreadTagPattern(), '_begin')                                

def makeExtension(configs=None):
    return I4pExtension(configs=configs)
