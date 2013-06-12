from operator import attrgetter
import random

from django.contrib.sites.models import Site
from django.http import Http404
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from tagging.managers import ModelTaggedItemManager
from tagging.models import TaggedItem, Tag
from tagging.utils import get_tag
from wiki.models import Article, ArticleForObject
from wiki.models import URLPath
from wiki.views.article import Edit
from wiki.core.exceptions import NoRootURL

from apps.project_sheet.models import I4pProject, ProjectMember

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

    @method_decorator(cache_page(60*60)) # One hour
    def dispatch(self, *args, **kwargs):
        return super(TagPageView, self).dispatch(*args, **kwargs)
    
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
                                                     I4pProject,
                                                     counts=True),
                       key=attrgetter('count'),
                   )
            )
        )[:15]

        # Get project sheets tagged with this tag XXX: site=site may
        # not be correct 4 Random projects with at least one picture.
        # It's not possible to mix distinct and order by random, so
        # use a trick
        hilighted_projects= TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            language_code=current_language_code,            
            master__site=current_site,
            master__pictures__isnull=False
        ).distinct(), tag_instance).distinct()
        context['picture_projects'] = random.sample(hilighted_projects, min(4, len(hilighted_projects)))


        # Mature projects
        mature_projects = TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            master__site=current_site,
            master__status__in=('WIP', 'END')
        ).distinct(), tag_instance).distinct()
        context['num_mature_projects_projects_with_tag']=len(mature_projects)
        context['mature_projects'] = random.sample(mature_projects, min(4, len(mature_projects)))

        # Starting projects
        starting_projects = TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            master__site=current_site,
            master__status__in=('IDEA', 'BEGIN')
        ).distinct(), tag_instance).distinct()
        context['num_starting_projects_projects_with_tag']=len(starting_projects)
        context['starting_projects'] = random.sample(starting_projects, min(4, len(starting_projects)))
         
        # New projects
        context['new_projects'] = TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            master__site=current_site,
        ).distinct(), tag_instance).order_by('-master__created')[:4]
        
        # Latest modifications
        context['modified_projects'] = TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            master__site=current_site,
        ).distinct(), tag_instance).order_by('-modified')[:4]

        # Related people
        # List is to force evaluation to avoid a sql bug in queryset combining later (project__in=projects)
        projects = list(TaggedItem.objects.get_by_model(I4pProject.objects.using_translations().filter(
            master__site=current_site,
        ).distinct(), tag_instance).all())
        # While we're at it, let's count them for free
        context['num_projects_with_tag']=len(projects)
        
        context['people'] = ProjectMember.objects.filter(
            project__in=projects
        ).order_by('?')[:6]

        return context

