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

from django.conf import settings

from piston.handler import BaseHandler

from apps.project_sheet.models import Answer, Objective, I4pProject, I4pProjectTranslation, Topic
from apps.project_sheet.utils import get_project_translations_from_parents

class I4pProjectTranslationHandler(BaseHandler):
    """
    Handler used to display informations about a project sheet.
    Use "project_id" GET parameter.
    """
    allowed_methods = ('GET',)
    model = I4pProjectTranslation
    project = None
    
    def read(self, request, project_id=None):
        # TODO: Check if class attributes doesn't have problems with threads on production
        if project_id is None:
            language_code = request.GET.get('lang', 'en')
            if language_code not in dict(settings.LANGUAGES) :
                language_code = "en"
            page = int(request.GET.get('page', 1)) - 1
            self.__class__.fields = (
              'id',
              'title',
              'baseline',
              ('project',(
                  ('location',(
                      'id',
                      'country'
                  )),
                  'best_of',
                  'status',
                  ('pictures',(
                      'id',
                      'thumb'
                  ))
              )),
            )
            # TODO: "pagination" in raw, change it to django standard 
            projects = I4pProject.objects.all()[page*10:page*10+10]
            list_projects = get_project_translations_from_parents(projects, language_code, "en", True)
            return list_projects
        else:
            self.__class__.project = I4pProjectTranslation.objects.get(pk=project_id)
            self.__class__.fields = (
              'id',
              'about_section',
              'baseline',
              'callto_section',
              'partners_section',
              ('project',(
                  'id',
                  'best_of',
                  'status',
                  ('location',(
                      'address',
                      'country'
                  )),
                  ('members',(
                      'fullname',
                      'username'
                  )),
                  'objective',
                  ('pictures',(
                      'author',
                      'created',
                      'desc',
                      'license',
                      'source',
                      'thumb',
                      'url'
                  )),
                  'questions',
                  ('references',(
                      'id',
                      'desc'
                  )),
                  ('videos',(
                      'id',
                      'video_url'
                  )),
                  'website'
              )),
              'themes',
              'title'
            )
            return self.__class__.project
    
    @classmethod
    def fullname(cls, anUser):
        return anUser.get_full_name()
    
    @classmethod
    def url(cls, anImageModel):
        return anImageModel.display.url
    
    @classmethod
    def questions(cls, anI4pProject):
        questions = []
        for topic in Topic.objects.language(I4pProjectTranslationHandler.project.language_code).filter(site_topics=anI4pProject.topics.all()):
            for question in topic.questions.language(I4pProjectTranslationHandler.project.language_code).all().order_by('weight'):
                answers = Answer.objects.language(I4pProjectTranslationHandler.project.language_code).filter(project=anI4pProject.id, question=question)
                questions.append({
                    "question": question.content,
                    "answer": answers and answers[0].content or None
                })
                
        return questions
    
    @classmethod
    def thumb(cls, anImageModel):
        return anImageModel.thumbnail_image.url
    
    # To get correct language for translated models
    @classmethod
    def objective(cls, anI4pProject):
        objectives = anI4pProject.objectives.language(I4pProjectTranslationHandler.project.language_code).all()
        return [{"name": objective.name} for objective in objectives]
