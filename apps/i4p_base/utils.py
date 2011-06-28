import unicodedata


def remove_accents(s):
    if isinstance(s, str):
        s = unicode(s, "utf8", "replace")
    s = unicodedata.normalize('NFD', s)
    return s.encode('ascii', 'ignore')
