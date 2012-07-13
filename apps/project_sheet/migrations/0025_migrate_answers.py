# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.sites.models import Site
from apps.project_sheet import models as ps

QUESTIONS = [
    ('uniqueness', dict(
        el=u"Με ποιους τρόπους είναι αυτό το έργο μοναδικό και δημιουργικό",
        en=u"in what ways is this project unique and creative",
        es=u"¿De qué manera este proyecto es único y creativo",
        fr=u"en quoi ce projet est-il singulier et créatif",
        it=u"in che modi il progetto è unico e creativo")),
    ('business_model', dict(
        el=u"Ποιο είναι το επιχειρηματικό μοντέλο του έργου",
        en=u"what is the business model of this project",
        es=u"¿Cuál es el modelo empresarial del proyecto",
        fr=u"Quel est le modèle économique de ce projet ",
        it=u"qual è il modello di business di questo progetto")),
    ('scalability', dict(
        el=u"Ποιες είναι οι δυνατότητες αυτού του έργου για την επέκταση και την ανάπτυξή του",
        en=u"what is the potential of this project to expand and develop",
        es=u"¿Qué potencial de expansión y desarrollo tiene este proyecto",
        fr=u"Quel est le potentiel de déploiement de cette initiative",
        it=u"qual è il potenziale di questo progetto di espandersi e svilupparsi")),
    ('value', dict(
        el=u"Ποιά είναι η κοινωνική αξία του έργου",
        en=u"What is the social value of this project",
        es=u"¿Cuál es el valor social de este proyecto",
        fr=u"Quelle est la plus-value sociale du projet",
        it=u"Qual è il valore sociale di questo progetto")),
    ('triggering_factor', dict(
        el=u"ποια ήταν η κινητήριος μοχλός του έργου",
        en=u"what was the triggering factor of this project",
        es=u"¿Qué factor puso en marcha este proyecto",
        fr=u"Quel a été le facteur déclenchant de ce projet ",
        it=u"qual è stato il fattore scatenante del progetto"))
]


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Patch up Sites for django-dynamicsites
        from django.db import connection, transaction, DatabaseError
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT folder_name FROM django_site")
        except DatabaseError:
            db.execute('ALTER TABLE django_site ADD COLUMN folder_name VARCHAR(255)')
        try:
            cursor.execute("SELECT subdomains FROM django_site")
        except DatabaseError:
            db.execute('ALTER TABLE django_site ADD COLUMN subdomains VARCHAR(255)')
 
        # Get the default site
        site = Site.objects.get(id=1)

        # Create a topic
        topic = ps.Topic(untranslated_name='Social Innovation')
        topic.translate('en')
        topic.label = 'Social Innovation'
        topic.save()
        topic.translate('fr')
        topic.label = 'Innovation sociale'
        topic.save()
        site_topic = ps.SiteTopic(site=site, topic=topic)
        site_topic.save()

        # Create questions
        questions = dict()

        for name, translations in QUESTIONS:
            questions[name] = ps.Question(topic=topic)
            for language, text in translations.items():
                questions[name].translate(language)
                questions[name].content = text
                questions[name].save()

        # Assign preexisting site data to the
        # default site and topic and migrate all answers
        for project in ps.I4pProject.objects.all():
            project.site.add(site)
            project.topics.add(site_topic)
            project.save()
            answers = dict()
            for translation in project.translations.all():
                for name, question in questions.items():
                    text = getattr(translation, '%s_section' % name)
                    if not text:
                        continue
                    if not name in answers:
                        answers[name] = ps.Answer(project=project,
                                                  question=questions[name])
                    answers[name].translate(translation.language_code)
                    answers[name].content = text
                    answers[name].save()


    def backwards(self, orm):
        pass


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'i4p_base.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'licenses.license': {
            'Meta': {'ordering': "('name',)", 'object_name': 'License'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'logo': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'licenses'", 'null': 'True', 'to': "orm['licenses.Organization']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'licenses.organization': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Organization'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'member.i4pprofile': {
            'Meta': {'object_name': 'I4pProfile'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'facebook': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5'}),
            'linkedin': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['i4p_base.Location']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'motto': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '15'}),
            'twitter': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'project_sheet.answer': {
            'Meta': {'unique_together': "(('question', 'project'),)", 'object_name': 'Answer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['project_sheet.I4pProject']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['project_sheet.Question']"})
        },
        'project_sheet.answertranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'AnswerTranslation'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['project_sheet.Answer']"})
        },
        'project_sheet.i4pproject': {
            'Meta': {'object_name': 'I4pProject'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['member.I4pProfile']", 'null': 'True', 'blank': 'True'}),
            'best_of': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['i4p_base.Location']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'through': "orm['project_sheet.ProjectMember']", 'to': "orm['auth.User']"}),
            'objectives': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['project_sheet.Objective']", 'null': 'True', 'blank': 'True'}),
            'project_leader_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['project_sheet.ProjectReference']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'IDEA'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project_sheet.SiteTopic']", 'symmetrical': 'False'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'project_sheet.i4pprojecttranslation': {
            'Meta': {'unique_together': "(('language_code', 'slug'),)", 'object_name': 'I4pProjectTranslation'},
            'about_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'baseline': ('django.db.models.fields.CharField', [], {'default': "u'One line description'", 'max_length': '180', 'null': 'True', 'blank': 'True'}),
            'business_model_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'callto_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'completion_progress': ('django.db.models.fields.CharField', [], {'default': "'EDIT'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'partners_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['project_sheet.I4pProject']"}),
            'scalability_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'themes': ('tagging.fields.TagField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'My Project Title'", 'max_length': '80'}),
            'triggering_factor_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'uniqueness_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'value_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'project_sheet.objective': {
            'Meta': {'object_name': 'Objective'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'project_sheet.objectivetranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ObjectiveTranslation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['project_sheet.Objective']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project_sheet.projectmember': {
            'Meta': {'unique_together': "(('project', 'user'),)", 'object_name': 'ProjectMember'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'detailed_members'", 'to': "orm['project_sheet.I4pProject']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_memberships'", 'to': "orm['auth.User']"})
        },
        'project_sheet.projectpicture': {
            'Meta': {'object_name': 'ProjectPicture'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('licenses.fields.LicenseField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pictures'", 'to': "orm['project_sheet.I4pProject']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'project_sheet.projectreference': {
            'Meta': {'object_name': 'ProjectReference'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'project_sheet.projectvideo': {
            'Meta': {'object_name': 'ProjectVideo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': "orm['project_sheet.I4pProject']"}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'project_sheet.question': {
            'Meta': {'object_name': 'Question'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['project_sheet.Topic']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'project_sheet.questiontranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'QuestionTranslation'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['project_sheet.Question']"})
        },
        'project_sheet.sitetopic': {
            'Meta': {'unique_together': "(('site', 'topic'),)", 'object_name': 'SiteTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'site_topics'", 'to': "orm['sites.Site']"}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'site_topics'", 'to': "orm['project_sheet.Topic']"})
        },
        'project_sheet.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()', 'db_index': 'True'}),
            'untranslated_name': ('django.db.models.fields.CharField', [], {'default': "'New topic'", 'max_length': '128'})
        },
        'project_sheet.topictranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'TopicTranslation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': "orm['project_sheet.Topic']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['project_sheet']
