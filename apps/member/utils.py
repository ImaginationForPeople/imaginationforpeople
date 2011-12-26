import re

from apps.i4p_base.utils import remove_accents

def fix_username(original_name):
    """
    Modify a username to comply with the site username policy, basically getting
    rid of accents, spaces and special characters.
    """
    username = re.sub("[^a-zA-Z0-9]", "", remove_accents(original_name))
    return username

