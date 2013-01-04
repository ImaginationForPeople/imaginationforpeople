from django import template
from apps.tags.models import TaggedCategory
from django.utils.safestring import mark_safe

register = template.Library()

class CategoriesTreeNode(template.Node):
    def __init__(self, caterories_root_name, search_state):
        self.caterories_root_name = caterories_root_name
        self.search_state_var = template.Variable(search_state)
    
    def render_node(self, node, search_state): 
        res= ""
        for child in node.children.all():
            res += '<li><a href="#SEARCH_URL#">%s</a>' % child.name
            if not child.children.count():
                res = res.replace("#SEARCH_URL#", search_state.add_tag(child.tag.name).full_url())
            else:
                res = res.replace("#SEARCH_URL#", "#")
                
            res += "<ul>" + self.render_node(child, search_state) + "</ul></li>"
        return res
    
    def render(self, context):
        root_node = TaggedCategory.objects.get(name=self.caterories_root_name)
        search_state = self.search_state_var.resolve(context)
        return mark_safe(self.render_node(root_node, search_state))
    
def categories_tree(parser, token):
    try:
        tag_name, caterories_root_name, search_state = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
    if not (caterories_root_name[0] == caterories_root_name[-1] and caterories_root_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return CategoriesTreeNode(caterories_root_name[1:-1], search_state)

register.tag('categories_tree', categories_tree)