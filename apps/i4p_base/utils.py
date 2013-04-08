#-- encoding: utf-8 --
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#
import datetime
from diff_match_patch import diff_match_patch    
import unicodedata

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser, User

from actstream.exceptions import check_actionable_model
from actstream.models import Action
from reversion.models import Version

def remove_accents(aString):
    """
    Remove accents from a string
    """
    if isinstance(aString, str):
        aString = unicode(aString, "utf8", "replace")
    aString = unicodedata.normalize('NFD', aString)
    return aString.encode('ascii', 'ignore')


#-- Activity stream utils --#
def action_create(actor, verb, action_object, target, description=None, public=True):
    """
    Handler function to create Action instance upon action signal call.
    """
    # Prevent AnonymousUser from not passing the checks
    if actor.is_anonymous():
        actor = User.objects.get(id=settings.ANONYMOUS_USER_ID)
    
    check_actionable_model(actor)
    check_actionable_model(action_object)
    check_actionable_model(target)
    
    newaction = Action(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=unicode(verb),
        target_object_id=target.id,
        target_content_type=ContentType.objects.get_for_model(target),
        action_object_object_id=action_object.id,
        action_object_content_type=ContentType.objects.get_for_model(action_object), 

        public=bool(public),
        description=description,
        timestamp=datetime.datetime.now(),
    )

    newaction.save()

    return newaction

# Reversion
def make_diffs_for_object(anObject, field_name, new_content):
    """
    Given an object and its field name, compare it to the new
    content and make diffs in arrays.
    """
    previous_objects = Version.objects.get_for_object(anObject).reverse()
    
    if len(previous_objects) > 0:
        previous_content = previous_objects[0].field_dict[field_name] or u""
    else:
        previous_content = u""
        
    dmp = diff_match_patch()
    return dmp.diff_main(unicode(previous_content), unicode(new_content))
        