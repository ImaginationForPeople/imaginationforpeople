from django.core.cache import cache
from django.contrib.auth.models import User

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


def lookup_ml_membership(workgroup):
    context = {}
    if workgroup.mailing_list:
        context['ml_member_list'] = [] # Both on I4P & the ML
        context['ml_nonmember_list'] = [] # Only subscribed to the ML
        members = get_ml_members(workgroup)
        emails = [member[0] for member in members]
        found_members = User.objects.filter(email__in=emails)
        for found_member in found_members:
            context['ml_member_list'].append(found_member)
            emails.remove(found_member.email)
            # Subscribe the user to the workgroup if not yet
            if found_member not in workgroup.subscribers.all():
                workgroup.subscribers.add(found_member)
        context['ml_nonmember_list'] = [User(email=nonmember_email) for nonmember_email in emails]
    return context