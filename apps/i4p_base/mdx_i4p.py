from markdown.inlinepatterns import SimpleTagPattern

from markdown import Extension
from markdown import etree

class ProjectTagPattern(SimpleTagPattern):
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\%([A-z][A-z])\%([\w-]+)', 'a')
        
    def handleMatch(self, m):
        from apps.project_sheet.models import I4pProjectTranslation # Don't move this to the top, it will circular imports
        el = etree.Element(self.tag)
        language = m.group(2)
        slug = m.group(3)
        try:
            project_translation = I4pProjectTranslation.objects.get(language_code=language, slug=slug)
            el.text = project_translation.title
            el.attrib['href'] = project_translation.get_absolute_url()
        except:
            el.text = "Unknown project (%s, %s)" % (language, slug)

        return el

class GroupTagPattern(SimpleTagPattern):
    def __init__(self):
        SimpleTagPattern.__init__(self, r'\+([\w-]+)', 'a')
        
    def handleMatch(self, m):
        from apps.workgroup.models import WorkGroup # Don't move this to the top, it will circular imports
        el = etree.Element(self.tag)
        group_slug = m.group(2)
        try:
            group = WorkGroup.objects.get(slug=group_slug)
            el.text = group.name
            el.attrib['href'] = group.get_absolute_url()
        except:
            el.text = "Unknown group (%s)" % (group_slug)

        return el
        
    
class I4pExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('grouppattern', GroupTagPattern(), '_begin')
        md.inlinePatterns.add('projectpattern', ProjectTagPattern(), '_begin')        

def makeExtension(configs=None):
    return I4pExtension(configs=configs)
