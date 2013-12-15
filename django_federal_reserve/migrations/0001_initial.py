# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Series'
        db.create_table(u'django_federal_reserve_series', (
            ('id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150, primary_key=True, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('units', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('frequency', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('seasonal_adjustment', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'django_federal_reserve', ['Series'])

        # Adding model 'Data'
        db.create_table(u'django_federal_reserve_data', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_federal_reserve.Series'])),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'django_federal_reserve', ['Data'])

        # Adding unique constraint on 'Data', fields ['series', 'date']
        db.create_unique(u'django_federal_reserve_data', ['series_id', 'date'])


    def backwards(self, orm):
        # Removing unique constraint on 'Data', fields ['series', 'date']
        db.delete_unique(u'django_federal_reserve_data', ['series_id', 'date'])

        # Deleting model 'Series'
        db.delete_table(u'django_federal_reserve_series')

        # Deleting model 'Data'
        db.delete_table(u'django_federal_reserve_data')


    models = {
        u'django_federal_reserve.data': {
            'Meta': {'unique_together': "(('series', 'date'),)", 'object_name': 'Data'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_federal_reserve.Series']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'django_federal_reserve.series': {
            'Meta': {'object_name': 'Series'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150', 'primary_key': 'True', 'db_index': 'True'}),
            'last_updated': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'seasonal_adjustment': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'units': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_federal_reserve']