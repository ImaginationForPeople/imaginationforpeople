from django.template import Library
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter

register = Library()

def truncate_chars(s, num):
    """
    Template filter to truncate a string to at most num characters respecting word
    boundaries.
    """
    s = force_unicode(s)
    length = int(num)
    if len(s) > length:
        length = length - 4
        if s[length-1] == ' ' or s[length] == ' ':
            s = s[:length].strip()
        else:
            words = s[:length].split()
            if len(words) > 1:
                del words[-1]
            s = u' '.join(words)
        s += ' ...'
    return s
truncate_chars = allow_lazy(truncate_chars, unicode)

def truncatechars(value, arg):
    """
    Truncates a string after a certain number of characters, but respects word boundaries.
    
    Argument: Number of characters to truncate after.
    """
    try:
        length = int(arg)
    except ValueError: # If the argument is not a valid integer.
        return value # Fail silently.
    return truncate_chars(value, length)
truncatechars.is_safe = True
truncatechars = stringfilter(truncatechars)

register.filter(truncatechars)