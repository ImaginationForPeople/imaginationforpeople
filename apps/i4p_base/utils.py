import unicodedata

def remove_accents(aString):
    """
    Remove accents from a string
    """
    if isinstance(aString, str):
        aString = unicode(aString, "utf8", "replace")
    aString = unicodedata.normalize('NFD', aString)
    return aString.encode('ascii', 'ignore')
