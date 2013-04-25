from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):
    def forwards(self, orm):
        # We happily have almost the same home made table schema for
        # handling multilingual models as hvad as. The only difference
        # is they called their superior relation "master" while we
        # named it "project". Just have to rename it so :)

        # Rename 'project' field to 'master'
        db.rename_column('project_sheet_i4pprojecttranslation', 'project_id', 'master_id')

    def backwards(self, orm):
        db.rename_column('project_sheet_i4pprojecttranslation', 'master_id', 'project_id')
