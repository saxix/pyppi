# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PythonVersion'
        db.create_table('pyppi_pythonversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('major', self.gf('django.db.models.fields.IntegerField')()),
            ('minor', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pyppi', ['PythonVersion'])

        # Adding unique constraint on 'PythonVersion', fields ['major', 'minor']
        db.create_unique('pyppi_pythonversion', ['major', 'minor'])

        # Adding model 'PlatformName'
        db.create_table('pyppi_platformname', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('pyppi', ['PlatformName'])

        # Adding model 'Architecture'
        db.create_table('pyppi_architecture', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=16, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('pyppi', ['Architecture'])

        # Adding model 'DistributionType'
        db.create_table('pyppi_distributiontype', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('pyppi', ['DistributionType'])

        # Adding model 'Classifier'
        db.create_table('pyppi_classifier', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
        ))
        db.send_create_signal('pyppi', ['Classifier'])

        # Adding model 'Package'
        db.create_table('pyppi_package', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, primary_key=True)),
            ('auto_hide', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_comments', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_protected', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pyppi', ['Package'])

        # Adding M2M table for field owners on 'Package'
        db.create_table('pyppi_package_owners', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['pyppi.package'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pyppi_package_owners', ['package_id', 'user_id'])

        # Adding M2M table for field maintainers on 'Package'
        db.create_table('pyppi_package_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['pyppi.package'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('pyppi_package_maintainers', ['package_id', 'user_id'])

        # Adding M2M table for field classifiers on 'Package'
        db.create_table('pyppi_package_classifiers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('package', models.ForeignKey(orm['pyppi.package'], null=False)),
            ('classifier', models.ForeignKey(orm['pyppi.classifier'], null=False))
        ))
        db.create_unique('pyppi_package_classifiers', ['package_id', 'classifier_id'])

        # Adding model 'Release'
        db.create_table('pyppi_release', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['pyppi.Package'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metadata_version', self.gf('django.db.models.fields.CharField')(default='1.0', max_length=64)),
            ('package_info', self.gf('pyppi.fields.PackageInfoField')()),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pyppi', ['Release'])

        # Adding unique constraint on 'Release', fields ['package', 'version']
        db.create_unique('pyppi_release', ['package_id', 'version'])

        # Adding model 'Distribution'
        db.create_table('pyppi_distribution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='distributions', to=orm['pyppi.Release'])),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('md5_digest', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('filetype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='distributions', to=orm['pyppi.DistributionType'])),
            ('pyversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='distributions', null=True, to=orm['pyppi.PythonVersion'])),
            ('platform', self.gf('django.db.models.fields.related.ForeignKey')(related_name='distributions', null=True, to=orm['pyppi.PlatformName'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('signature', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('pyppi', ['Distribution'])

        # Adding unique constraint on 'Distribution', fields ['release', 'filetype', 'pyversion']
        db.create_unique('pyppi_distribution', ['release_id', 'filetype_id', 'pyversion_id'])

        # Adding model 'Review'
        db.create_table('pyppi_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reviews', to=orm['pyppi.Release'])),
            ('rating', self.gf('django.db.models.fields.PositiveSmallIntegerField')(blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('pyppi', ['Review'])

        # Adding model 'MasterIndex'
        db.create_table('pyppi_masterindex', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pyppi', ['MasterIndex'])

        # Adding model 'MirrorLog'
        db.create_table('pyppi_mirrorlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['pyppi.MasterIndex'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default='now')),
        ))
        db.send_create_signal('pyppi', ['MirrorLog'])

        # Adding M2M table for field releases_added on 'MirrorLog'
        db.create_table('pyppi_mirrorlog_releases_added', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mirrorlog', models.ForeignKey(orm['pyppi.mirrorlog'], null=False)),
            ('release', models.ForeignKey(orm['pyppi.release'], null=False))
        ))
        db.create_unique('pyppi_mirrorlog_releases_added', ['mirrorlog_id', 'release_id'])

        # Adding model 'IPRestriction'
        db.create_table('pyppi_iprestriction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='iprestrictions', to=orm['auth.User'])),
            ('only_allowed_from', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('pyppi', ['IPRestriction'])

        # Adding model 'KnownHost'
        db.create_table('pyppi_knownhost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('pyppi', ['KnownHost'])

        # Adding M2M table for field packages on 'KnownHost'
        db.create_table('pyppi_knownhost_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('knownhost', models.ForeignKey(orm['pyppi.knownhost'], null=False)),
            ('package', models.ForeignKey(orm['pyppi.package'], null=False))
        ))
        db.create_unique('pyppi_knownhost_packages', ['knownhost_id', 'package_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Distribution', fields ['release', 'filetype', 'pyversion']
        db.delete_unique('pyppi_distribution', ['release_id', 'filetype_id', 'pyversion_id'])

        # Removing unique constraint on 'Release', fields ['package', 'version']
        db.delete_unique('pyppi_release', ['package_id', 'version'])

        # Removing unique constraint on 'PythonVersion', fields ['major', 'minor']
        db.delete_unique('pyppi_pythonversion', ['major', 'minor'])

        # Deleting model 'PythonVersion'
        db.delete_table('pyppi_pythonversion')

        # Deleting model 'PlatformName'
        db.delete_table('pyppi_platformname')

        # Deleting model 'Architecture'
        db.delete_table('pyppi_architecture')

        # Deleting model 'DistributionType'
        db.delete_table('pyppi_distributiontype')

        # Deleting model 'Classifier'
        db.delete_table('pyppi_classifier')

        # Deleting model 'Package'
        db.delete_table('pyppi_package')

        # Removing M2M table for field owners on 'Package'
        db.delete_table('pyppi_package_owners')

        # Removing M2M table for field maintainers on 'Package'
        db.delete_table('pyppi_package_maintainers')

        # Removing M2M table for field classifiers on 'Package'
        db.delete_table('pyppi_package_classifiers')

        # Deleting model 'Release'
        db.delete_table('pyppi_release')

        # Deleting model 'Distribution'
        db.delete_table('pyppi_distribution')

        # Deleting model 'Review'
        db.delete_table('pyppi_review')

        # Deleting model 'MasterIndex'
        db.delete_table('pyppi_masterindex')

        # Deleting model 'MirrorLog'
        db.delete_table('pyppi_mirrorlog')

        # Removing M2M table for field releases_added on 'MirrorLog'
        db.delete_table('pyppi_mirrorlog_releases_added')

        # Deleting model 'IPRestriction'
        db.delete_table('pyppi_iprestriction')

        # Deleting model 'KnownHost'
        db.delete_table('pyppi_knownhost')

        # Removing M2M table for field packages on 'KnownHost'
        db.delete_table('pyppi_knownhost_packages')


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
        'pyppi.architecture': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Architecture'},
            'key': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'pyppi.classifier': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Classifier'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'pyppi.distribution': {
            'Meta': {'unique_together': "(('release', 'filetype', 'pyversion'),)", 'object_name': 'Distribution'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'distributions'", 'to': "orm['pyppi.DistributionType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5_digest': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'platform': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'distributions'", 'null': 'True', 'to': "orm['pyppi.PlatformName']"}),
            'pyversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'distributions'", 'null': 'True', 'to': "orm['pyppi.PythonVersion']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'distributions'", 'to': "orm['pyppi.Release']"}),
            'signature': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'pyppi.distributiontype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DistributionType'},
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'pyppi.iprestriction': {
            'Meta': {'object_name': 'IPRestriction'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'only_allowed_from': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'iprestrictions'", 'to': "orm['auth.User']"})
        },
        'pyppi.knownhost': {
            'Meta': {'object_name': 'KnownHost'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['pyppi.Package']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'pyppi.masterindex': {
            'Meta': {'object_name': 'MasterIndex'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pyppi.mirrorlog': {
            'Meta': {'object_name': 'MirrorLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': "'now'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': "orm['pyppi.MasterIndex']"}),
            'releases_added': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'mirror_sources'", 'blank': 'True', 'to': "orm['pyppi.Release']"})
        },
        'pyppi.package': {
            'Meta': {'ordering': "['name']", 'object_name': 'Package'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auto_hide': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['pyppi.Classifier']", 'symmetrical': 'False'}),
            'is_protected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'packages_maintained'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'primary_key': 'True'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'packages_owned'", 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'pyppi.platformname': {
            'Meta': {'ordering': "('name',)", 'object_name': 'PlatformName'},
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'pyppi.pythonversion': {
            'Meta': {'ordering': "('major', 'minor')", 'unique_together': "(('major', 'minor'),)", 'object_name': 'PythonVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'major': ('django.db.models.fields.IntegerField', [], {}),
            'minor': ('django.db.models.fields.IntegerField', [], {})
        },
        'pyppi.release': {
            'Meta': {'ordering': "['-created']", 'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_version': ('django.db.models.fields.CharField', [], {'default': "'1.0'", 'max_length': '64'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['pyppi.Package']"}),
            'package_info': ('pyppi.fields.PackageInfoField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'pyppi.review': {
            'Meta': {'object_name': 'Review'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {'blank': 'True'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': "orm['pyppi.Release']"})
        }
    }

    complete_apps = ['pyppi']