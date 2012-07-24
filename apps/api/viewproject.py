# -*- encoding: utf-8 -*-
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

from django.contrib.auth.models import User

from piston.handler import BaseHandler

from apps.project_sheet.models import Answer, I4pProject, I4pProjectTranslation, Location, Objective, ProjectPicture, ProjectReference, ProjectVideo, Topic

class I4pProjectTranslationHandler(BaseHandler):
    """
    Handler used to display informations about a project sheet.
    Use "project_id" GET parameter.
    """
    allowed_methods = ('GET',)
    model = I4pProjectTranslation
    project_id = 0
    fields = ('about_section', 'baseline', 'callto_section', 'completion_progress', 'partners_section', 'project', 'themes', 'title')
    
    def read(self, request, project_id):
        # TODO: Check if class attributes doesn't have problems with threads on production
        self.__class__.project_id = project_id
        return I4pProjectTranslation.objects.get(pk=project_id)
    
class I4pProjectHandler(BaseHandler):
    model = I4pProject
    fields = ('id', 'location', 'members', 'objectives',  'pictures', 'questions', 'references', 'videos', 'website')
    
    @classmethod
    def questions(cls, model):
        questions = []
        for topic in Topic.objects.filter(site_topics=model.topics.all()):
            for question in topic.questions.all().order_by('weight'):
                answers = Answer.objects.filter(project=model.id, question=question)
                questions.append({
                    "question": question.content,
                    "answer": answers and answers[0].content or None
                })
                
        return questions
    
class LocationHandler(BaseHandler):
    model = Location
    fields = ('address', 'country')
    
class ObjectiveHandler(BaseHandler):
    model = Objective
    fields = ('id', 'name')

class ProjectPicture(BaseHandler):
    model = ProjectPicture
    fields = ('author', 'created', 'desc', 'license', 'source', 'url')
    
    @classmethod
    def url(cls, model):
        return model.display.url

class ProjectReferenceHandler(BaseHandler):
    model = ProjectReference
    fields = ('id', 'desc')

class ProjectVideoHandler(BaseHandler):
    model = ProjectVideo
    fields = ('id', 'video_url')

class UserHandler(BaseHandler):
    model = User
    fields = ('fullname', 'username')
    
    @classmethod
    def fullname(cls, model):
        return model.get_full_name() or None
