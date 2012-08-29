from operator import attrgetter
import random

from django.contrib.sites.models import Site
from django.http import Http404
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from tagging.managers import ModelTaggedItemManager
from tagging.models import TaggedItem, Tag
from tagging.utils import get_tag
from wiki.models import Article, ArticleForObject
from wiki.models import URLPath
from wiki.views.article import Edit
from wiki.core.exceptions import NoRootURL

from apps.project_sheet.models import I4pProjectTranslation, ProjectMember

class TagEditWikiView(Edit):
    template_name = 'tags/wiki_edit.html'

    def dispatch(self, request, tag, *args, **kwargs):
        self.tag = get_tag(tag)        
        article = Article.get_for_object(self.tag)
        return super(TagEditWikiView, self).dispatch(request, article_id=article.id, *args, **kwargs)

    def get_success_url(self):
        return redirect('tags:tag-view', self.tag)
        
    def get_context_data(self, **kwargs):
        kwargs['tag_instance'] = self.tag
        return Edit.get_context_data(self, **kwargs)

class TagPageView(TemplateView):
    template_name = 'tags/tag_view.html'

    def get_context_data(self, tag, **kwargs):
        context = super(TagPageView, self).get_context_data(**kwargs)

        current_site = Site.objects.get_current()
        current_language_code = translation.get_language()

        tag_instance = get_tag(tag)
        if tag_instance is None:
            raise Http404(_('No Tag found matching "%s".') % tag)

        try:
            article = Article.get_for_object(tag_instance)
        except ArticleForObject.DoesNotExist:
            # Get or create root
            try:
                root_path = URLPath.root()
            except NoRootURL:
                root_path = URLPath.create_root(site=current_site)

            # Get current language namespace. E.g. "/fr"
            try:
                language_ns_path = URLPath.get_by_path("/%s" % current_language_code)
            except URLPath.DoesNotExist:
                language_ns_path = URLPath.create_article(
                    parent=root_path,
                    slug=current_language_code,
                    site=current_site,
                    title=current_language_code
                )

            # Get or create the article
            from django.template.defaultfilters import slugify                
            tag_slug = slugify(tag_instance.name)
            try:
                article_path = URLPath.get_by_path("/%s/%s" % (current_language_code,
                                                               tag_slug)
                                                   )
            except URLPath.DoesNotExist:
                article_path = URLPath.create_article(
                    parent=language_ns_path,
                    slug=tag_slug,
                    site=current_site,
                    title=tag_instance.name
                )

            # Get the wiki article itself
            article = article_path.article
            article.add_object_relation(tag_instance)

        context['article'] = article

        # XXX: site not taken in account        
        context['tag'] = tag_instance
        context['related_tags'] = list(
            reversed(
                sorted(Tag.objects.related_for_model(tag_instance, 
                                                     I4pProjectTranslation,
                                                     counts=True),
                       key=attrgetter('count'),
                   )
            )
        )[:15]

        # Get project sheets tagged with this tag XXX: site=site may
        # not be correct 4 Random projects with at least one picture.
        # It's not possible to mix distinct and order by random, so
        # use a trick
        hilighted_projects= TaggedItem.objects.get_by_model(I4pProjectTranslation.objects.filter(
            language_code=current_language_code,            
            project__site=current_site,
            project__pictures__isnull=False
        ).distinct(), tag_instance).distinct()
        context['picture_project_translations'] = [random.choice(hilighted_projects) for i in range(4)]


        # Mature projects
        mature_project_translations = TaggedItem.objects.get_by_model(I4pProjectTranslation.objects.filter(
            language_code=current_language_code,
            project__site=current_site,
            project__status__in=('WIP', 'END')
        ).distinct(), tag_instance)
        context['mature_project_translations'] = [random.choice(mature_project_translations) for i in range(4)]        

        # Starting projects
        starting_project_translations = TaggedItem.objects.get_by_model(I4pProjectTranslation.objects.filter(
            language_code=current_language_code,            
            project__site=current_site,
            project__status__in=('IDEA', 'BEGIN')
        ).distinct(), tag_instance)
        context['starting_project_translations'] = [random.choice(starting_project_translations) for i in range(4)]
         
        # New projects
        context['new_project_translations'] = TaggedItem.objects.get_by_model(I4pProjectTranslation.objects.filter(
            language_code=current_language_code,            
            project__site=current_site,
        ).distinct(), tag_instance).order_by('-project__created')[:4]
        
        # Latest modifications
        context['modified_project_translations'] = TaggedItem.objects.get_by_model(I4pProjectTranslation.objects.filter(
            language_code=current_language_code,            
            project__site=current_site,
        ).distinct(), tag_instance).order_by('-modified')[:4]

        # Related people
        project_translations = ModelTaggedItemManager().with_any([tag_instance.name],
                                                                 I4pProjectTranslation.objects.filter(
                                                                     language_code=current_language_code,
                                                                     project__site=current_site,
                                                                 )
                                                             ).distinct()
        projects = [p.project for p in project_translations]
        
        context['people'] = ProjectMember.objects.filter(
            project__in=projects
        ).order_by('?')[:6]

        # XXX Need to remove duplicates

        return context

