from django import template
from filelibrary.models import FileCategory

register = template.Library()

class FileCategoryListNode(template.Node):
    """ template node that returns the advertisement list that filters by current url path and ad type"""
    def __init__(self, as_variable_name):
        self.as_variable_name = as_variable_name

    def render(self, context):
        #instance = self.instance_resolver.resolve(context)
        context[self.as_variable_name] = FileCategory.objects.live()
        return ''

@register.tag # this is just like register.tag('current_time', do_current_time)
def file_category_list(context, args):
    tag_template_syntax = "Tag's syntax is {%% %s as \"<context_variable_name>\" %%}"
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, as_token, as_variable_name = args.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(tag_template_syntax % args.contents.split()[0])
    if not (as_variable_name[0] == as_variable_name[-1] and as_variable_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError("Argument is not in quotes. " + tag_template_syntax % tag_name)
    as_variable_name = as_variable_name.replace("\"", "").replace("\'", "")
    return FileCategoryListNode(as_variable_name)
