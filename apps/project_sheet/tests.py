"""
Example on how to use tests for TDD
"""
from django.test import TestCase
from django.http import QueryDict
from apps.project_sheet.models import I4pProject, I4pProjectTranslation

from .utils import create_parent_project, get_project_translation_by_slug
from .utils import get_project_translation_from_parent, get_project_translations_from_parents
from .utils import create_project_translation, get_or_create_project_translation_by_slug
from .utils import get_or_create_project_translation_from_parent
from .filters import ThemesFilterForm, FilterSet


class TestUtils(TestCase):
    fixtures = ["test_pjsheet"]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_parent_project(self):
        project = create_parent_project()
        self.assertTrue(project.pk > 0)


    def test_get_project_translation_by_slug(self):
        # Existing project
        translation = get_project_translation_by_slug('boby-a-la-mer', 'fr')
        self.assertEqual(translation.slug, 'boby-a-la-mer')

        # Existing slug but not in this language
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_by_slug,
                          (),
                          {'project_translation_slug': 'boby-a-la-mer',
                           'language_code': 'en'}
                          )

        # Non-existent slug (in any language)
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_by_slug,
                          (),
                          {'project_translation_slug': 'non-existent-slug',
                           'language_code': 'en'}
                          )


        # Existing slug but incorrect language
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_by_slug,
                          (),
                          {'project_translation_slug': 'boby-a-la-mer',
                           'language_code': 'kk'}
                          )

        # Non-existing slug and incorrect language
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_by_slug,
                          project_translation_slug='non-existing-slug',
                          language_code='kk'
                          )


    def test_project_translation_from_parent(self):
        # Get an existing translation and project
        translation_fr = get_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                         language_code='fr')
        parent = translation_fr.project

        # Existing one
        requested_translation = get_project_translation_from_parent(parent=parent,
                                                                    language_code='fr')
        self.assertEqual(translation_fr, requested_translation)

        # If two translations have the same slug, make sure the
        # correct one is returned
        requested_translation = get_project_translation_from_parent(parent=parent,
                                                                    language_code='zh')
        self.assertNotEqual(translation_fr, requested_translation)

        # Non-existing one in the given language, no fallback
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_from_parent,
                          parent=parent,
                          language_code='kk',
                          )

        # Non-existing one in the given language but in the fallback language
        requested_translation = get_project_translation_from_parent(parent=parent,
                                                                    language_code='kk',
                                                                    fallback_language='fr')
        self.assertEqual(requested_translation, translation_fr)

        # Non-existing one in the given language neither in the fallback language
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translation_from_parent,
                          parent=parent,
                          language_code='kk',
                          fallback_language='en'
                          )

        # Parent is None
        self.assertRaises(I4pProject.DoesNotExist,
                          get_project_translation_from_parent,
                          parent=None,
                          language_code='fr',
                          )

        # If both the language code and the fallback language don't
        # exist, make sure fallback_any works.
        requested_translation = get_project_translation_from_parent(parent=parent,
                                                                    language_code='kk',
                                                                    fallback_language='pm',
                                                                    fallback_any=True)

        self.assertTrue(isinstance(requested_translation, I4pProjectTranslation))
        self.assertEqual(requested_translation.project, parent)


    def test_get_project_translations_from_parents(self):
        projects = I4pProject.objects.all()

        # Get ONLY translations in french. All projects have a french
        # translation so it has to work.
        translations = get_project_translations_from_parents(parents_qs=projects,
                                                             language_code='fr',
                                                             fallback_language=None,
                                                             fallback_any=False)


        # Get translations in language 'kk'. This language does not exist.
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translations_from_parents,
                          parents_qs=projects,
                          language_code='kk',
                          fallback_language=None,
                          fallback_any=False)

        # Get translations in language 'zh'. Some sheets are not in
        # chinese, so it should raise an exception.
        self.assertRaises(I4pProjectTranslation.DoesNotExist,
                          get_project_translations_from_parents,
                          parents_qs=projects,
                          language_code='kk',
                          fallback_language=None,
                          fallback_any=False)


        # Get translations in chinese ('zh') and in french if not found
        translations = get_project_translations_from_parents(parents_qs=projects,
                                                             language_code='zh',
                                                             fallback_language='fr',
                                                             fallback_any=False)

        # Get translation in french or english or any
        translations = get_project_translations_from_parents(parents_qs=projects,
                                                             language_code='fr',
                                                             fallback_language='en',
                                                             fallback_any=True
                                                             )


    def test_create_project_translation(self):
        ## Tests with no parent project

        # Create a new project sheet in french with a slug
        project_translation = create_project_translation(language_code='fr',
                                                         parent_project=None,
                                                         default_title='new-project')

        self.assertEqual(project_translation.slug, 'new-project')
        self.assertTrue(project_translation.pk > 0)

        # Try to create it again, the slug and model should be different
        second_project_translation = create_project_translation(language_code='fr',
                                                                parent_project=None,
                                                                default_title='new-project')

        self.assertTrue(project_translation.pk > 0)
        self.assertNotEqual(project_translation.slug, second_project_translation.slug)
        self.assertEqual(second_project_translation.slug, 'new-project-2')

        self.assertNotEqual(project_translation.pk, second_project_translation.pk)

        # Create a project translation but with no given slug
        project_translation = create_project_translation(language_code='fr',
                                                         parent_project=None)

        self.assertTrue(project_translation.pk > 0)

        ## Tests with parent project
        project_translation = get_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                              language_code='fr')

        project = project_translation.project

        # Request to create a translation that already exists. That should fail.
        self.assertRaises(Exception,
                          create_project_translation,
                          language_code='fr',
                          parent_project=project)

        self.assertEqual(len([t for t in project.translations.all() if t.language_code == 'fr']), 1)


        # Request to create a new translation
        requested_translation = create_project_translation(language_code='es',
                                                           parent_project=project)

        self.assertTrue(requested_translation.pk > 0)
        self.assertEqual(requested_translation.language_code, 'es')
        self.assertEqual(requested_translation.project, project)


    def test_get_or_create_project_translation_by_slug(self):
        project_translation = get_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                              language_code='fr')

        project = project_translation.project

        # Request to get or create a translation that already exists.
        requested_translation = get_or_create_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                                          language_code='fr')

        self.assertEqual(len([t for t in project.translations.all() if t.language_code == 'fr']), 1)
        self.assertEqual(requested_translation, project_translation)

        # Request to get or create a translation that does not exist
        new_translation = get_or_create_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                                    language_code='en',
                                                                    parent_project=project,
                                                                    default_title='Boby at the sea')

        self.assertEqual(len([t for t in project.translations.all() if t.language_code == 'en']), 1)
        self.assertEqual(new_translation.slug, 'boby-a-la-mer')
        self.assertEqual(new_translation.project, project)


    def test_get_or_create_project_translation_from_parent(self):
        project_translation = get_project_translation_by_slug(project_translation_slug='boby-a-la-mer',
                                                              language_code='fr')

        project = project_translation.project


        # already existing translation
        requested_translation = get_or_create_project_translation_from_parent(parent_project=project,
                                                                              language_code='fr')

        self.assertEqual(len([t for t in project.translations.all() if t.language_code == 'fr']), 1)
        self.assertEqual(requested_translation, project_translation)

        # new translation
        new_translation = get_or_create_project_translation_from_parent(parent_project=project,
                                                                        language_code='pt',
                                                                        default_title='New One')

        self.assertEqual(len([t for t in project.translations.all() if t.language_code == 'pt']), 1)
        self.assertEqual(new_translation.slug, 'new-one')
        self.assertEqual(new_translation.project, project)



class TestFilters(TestCase):
    fixtures = ["test_pjsheet"]


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_themes_filter(self):

        # "themes" param must be a list of comma separated integer
        theme_filter = ThemesFilterForm(QueryDict('themes=Coin'))
        self.assertFalse(theme_filter.is_valid())

        theme_filter = ThemesFilterForm(QueryDict('themes=Coin,Plop'))
        self.assertFalse(theme_filter.is_valid())

        theme_filter = ThemesFilterForm(QueryDict('themes=Coin,1'))
        self.assertFalse(theme_filter.is_valid())

        theme_filter = ThemesFilterForm(QueryDict('themes=1,2')) #"tag Coin"
        self.assertTrue(theme_filter.is_valid())

        #Normal filtering
        theme_filter = ThemesFilterForm(QueryDict('themes=1')) #"tag Coin"
        self.assertTrue(theme_filter.is_valid())

        filters = FilterSet([theme_filter])

        result = filters.apply_to(queryset=I4pProjectTranslation.objects.all())
        self.assertEqual(result.count(), 1)
        self.assertTrue(isinstance(result[0], I4pProjectTranslation))

        # No filter return the same queryset as in input
        theme_filter = ThemesFilterForm(QueryDict('themes='))
        filters = FilterSet([theme_filter])

        self.assertEquals(filters.is_valid(), theme_filter.is_valid())

        queryset = I4pProjectTranslation.objects.all()
        result = filters.apply_to(queryset=queryset)
        self.assertEquals(result, queryset)










