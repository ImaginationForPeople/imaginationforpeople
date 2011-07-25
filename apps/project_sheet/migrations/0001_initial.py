# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ProjectReference'
        db.create_table('project_sheet_projectreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('project_sheet', ['ProjectReference'])

        # Adding model 'I4pProject'
        db.create_table('project_sheet_i4pproject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['member.I4pProfile'], null=True, blank=True)),
            ('ip_addr', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('objective', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('project_leader_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['i4p_base.Location'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('project_sheet', ['I4pProject'])

        # Adding M2M table for field references on 'I4pProject'
        db.create_table('project_sheet_i4pproject_references', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('i4pproject', models.ForeignKey(orm['project_sheet.i4pproject'], null=False)),
            ('projectreference', models.ForeignKey(orm['project_sheet.projectreference'], null=False))
        ))
        db.create_unique('project_sheet_i4pproject_references', ['i4pproject_id', 'projectreference_id'])

        # Adding model 'I4pProjectTranslation'
        db.create_table('project_sheet_i4pprojecttranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['project_sheet.I4pProject'])),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'My Project Title', max_length=80)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None, db_index=True)),
            ('baseline', self.gf('django.db.models.fields.CharField')(default=u'One line description', max_length=180, null=True, blank=True)),
            ('about_section', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('uniqueness_section', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('value_section', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('scalability_section', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('themes', self.gf('tagging.fields.TagField')(null=True)),
        ))
        db.send_create_signal('project_sheet', ['I4pProjectTranslation'])

        # Adding unique constraint on 'I4pProjectTranslation', fields ['project', 'language_code', 'slug']
        db.create_unique('project_sheet_i4pprojecttranslation', ['project_id', 'language_code', 'slug'])

        # Adding model 'ProjectPicture'
        db.create_table('project_sheet_projectpicture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('original_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pictures', to=orm['project_sheet.I4pProject'])),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            #('license', self.gf('licenses.fields.LicenseField')()),
            ('license', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['licenses.License'], null=True, blank=True)),
        ))
        db.send_create_signal('project_sheet', ['ProjectPicture'])

        # Adding model 'ProjectVideo'
        db.create_table('project_sheet_projectvideo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='videos', to=orm['project_sheet.I4pProject'])),
        ))
        db.send_create_signal('project_sheet', ['ProjectVideo'])

        # Adding model 'ProjectMember'
        db.create_table('project_sheet_projectmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='detailed_members', to=orm['project_sheet.I4pProject'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='project_memberships', to=orm['auth.User'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('project_sheet', ['ProjectMember'])

        # Adding unique constraint on 'ProjectMember', fields ['project', 'user']
        db.create_unique('project_sheet_projectmember', ['project_id', 'user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ProjectMember', fields ['project', 'user']
        db.delete_unique('project_sheet_projectmember', ['project_id', 'user_id'])

        # Removing unique constraint on 'I4pProjectTranslation', fields ['project', 'language_code', 'slug']
        db.delete_unique('project_sheet_i4pprojecttranslation', ['project_id', 'language_code', 'slug'])

        # Deleting model 'ProjectReference'
        db.delete_table('project_sheet_projectreference')

        # Deleting model 'I4pProject'
        db.delete_table('project_sheet_i4pproject')

        # Removing M2M table for field references on 'I4pProject'
        db.delete_table('project_sheet_i4pproject_references')

        # Deleting model 'I4pProjectTranslation'
        db.delete_table('project_sheet_i4pprojecttranslation')

        # Deleting model 'ProjectPicture'
        db.delete_table('project_sheet_projectpicture')

        # Deleting model 'ProjectVideo'
        db.delete_table('project_sheet_projectvideo')

        # Deleting model 'ProjectMember'
        db.delete_table('project_sheet_projectmember')


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
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '4'}),
            'linkedin': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['i4p_base.Location']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'motto': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'twitter': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'project_sheet.i4pproject': {
            'Meta': {'object_name': 'I4pProject'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['member.I4pProfile']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['i4p_base.Location']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'through': "orm['project_sheet.ProjectMember']", 'to': "orm['auth.User']"}),
            'objective': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'project_leader_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['project_sheet.ProjectReference']", 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'project_sheet.i4pprojecttranslation': {
            'Meta': {'unique_together': "(('project', 'language_code', 'slug'),)", 'object_name': 'I4pProjectTranslation'},
            'about_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'baseline': ('django.db.models.fields.CharField', [], {'default': "u'One line description'", 'max_length': '180', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['project_sheet.I4pProject']"}),
            'scalability_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'themes': ('tagging.fields.TagField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'My Project Title'", 'max_length': '80'}),
            'uniqueness_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'value_section': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'project_sheet.projectmember': {
            'Meta': {'unique_together': "(('project', 'user'),)", 'object_name': 'ProjectMember'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True'}),
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
        }
    }

    complete_apps = ['project_sheet']
