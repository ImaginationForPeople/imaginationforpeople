from django.core.cache import cache

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
