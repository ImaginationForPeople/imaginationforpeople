# vim: set noai ts=4 sw=4 et:

from django import template

register = template.Library()

@register.tag(name='unique_counter')
def do_unique_counter(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)

    except ValueError:
        raise template.TemplateSyntaxError("'unique_counter' node requires a variable name.")
    return UniqueCounterNode(args)

class UniqueCounterNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            var = template.resolve_variable(self.varname, context)
        except:
            var = 0
        deep = len(context.dicts)-1
        context.dicts[deep][self.varname] = var+1
        return ''
        #return "%d" % (var)

