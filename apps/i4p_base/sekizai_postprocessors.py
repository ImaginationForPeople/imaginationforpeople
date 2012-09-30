from compressor.templatetags.compress import CompressorNode
from django.template.base import Template

def compress(context, data, name):
    """
    Data is the string from the template (the list of js files in this case)
    Name is either 'js' or 'css' (the sekizai namespace)

    We basically just manually pass the string through the {% compress 'js' %} template tag
    """
    return CompressorNode(nodelist=Template(data).nodelist, kind=name, mode='file').render(context=context)