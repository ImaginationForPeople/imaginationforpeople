from django.core.cache import cache
from apps.project_sheet.models import I4pProjectTranslation
from tagging.models import Tag

def get_ml_members(workgroup):
    """
    Get Mailing list members
    """
    cache_key = '%s-ml-members' % workgroup.slug
    res = cache.get(cache_key, None)
    if not res:
        res = workgroup.mailing_list.get_all_members()
        cache.set(cache_key, res, 3600)
        
    return res

def gen_tag_list():
    tags = Tag.objects.usage_for_model(I4pProjectTranslation, counts=True)
    tags_return = []
    for tag in tags:
        tagtoadd = (tag.name, tag)
        tags_return.append(tagtoadd)
        
    return tags_return
