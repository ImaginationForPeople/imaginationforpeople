from django import template
from django.contrib.contenttypes.models import ContentType

from apps.forum.models import SpecificQuestion
from apps.workgroup.models import WorkGroup

register = template.Library()

class WorkgroupsNode(template.Node):
    def __init__(self, thread_var_name, workgroup_var_name):
        self.thread_var = template.Variable(thread_var_name)
        self.workgroup_var_name = workgroup_var_name
        
    def render(self, context):
        thread = self.thread_var.resolve(context)
        specific_questions = SpecificQuestion.objects.filter(type__type="wg-discuss",
                                                             thread=thread,
                                                             content_type=ContentType.objects.get_for_model(WorkGroup))
        context[self.workgroup_var_name] = [q.context_object for q in specific_questions]
        return ''

import re
def workgroups(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    thread_var_name, workgroup_var_name = m.groups()
    return WorkgroupsNode(thread_var_name, workgroup_var_name)

register.tag("workgroups", workgroups)
