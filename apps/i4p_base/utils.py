import unicodedata


def remove_accents(str):
    nkfd_form = unicodedata.normalize('NFKD', str.decode("utf-8"))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
