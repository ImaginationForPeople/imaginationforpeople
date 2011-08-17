# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WorkGroup'
        db.create_table('workgroup_workgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('mailing_list', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['django_mailman.List'], null=True, blank=True)),
        ))
        db.send_create_signal('workgroup', ['WorkGroup'])


    def backwards(self, orm):
        
        # Deleting model 'WorkGroup'
        db.delete_table('workgroup_workgroup')


    models = {
        'django_mailman.list': {
            'Meta': {'object_name': 'List'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'encoding': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'workgroup.workgroup': {
            'Meta': {'object_name': 'WorkGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'mailing_list': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['django_mailman.List']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'})
        }
    }

    complete_apps = ['workgroup']
