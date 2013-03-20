from django import template
from apps.tags.models import TaggedCategory
from django.utils.safestring import mark_safe

register = template.Library()

class CategoriesTreeNode(template.Node):
    def __init__(self, root, search_state):
        self.root_var = template.Variable(root)
        self.search_state_var = template.Variable(search_state)
    
    def render_node(self, node, search_state): 
        res= ""
        for child in node.children.all():
            if not search_state :
                res += '<li><a id="%s" class="tag-selector" href="">%s</a>' % (child.id, child.name)
            else:
                res += '<li><a class="tag-selector" href="#SEARCH_URL#">%s</a>' % child.name
                
            if not child.children.count() and search_state:
                res = res.replace("#SEARCH_URL#", search_state.add_tag(child.tag.name).full_url())
            else:
                res = res.replace("#SEARCH_URL#", "#")
            
            tmp = self.render_node(child, search_state)
            if tmp:
                res += "<ul>" + tmp + "</ul></li>"
        return res
    
    def render(self, context):
        root = self.root_var.resolve(context)
        search_state = self.search_state_var.resolve(context)
        return mark_safe(self.render_node(root, search_state))
    
def categories_tree(parser, token):
    try:
        tag_name, root, search_state = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
    return CategoriesTreeNode(root, search_state)

register.tag('categories_tree', categories_tree)