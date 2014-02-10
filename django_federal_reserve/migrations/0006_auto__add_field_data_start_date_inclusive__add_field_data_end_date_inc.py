# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Data.start_date_inclusive'
        db.add_column(u'django_federal_reserve_data', 'start_date_inclusive',
                      self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Data.end_date_inclusive'
        db.add_column(u'django_federal_reserve_data', 'end_date_inclusive',
                      self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Data.start_date_inclusive'
        db.delete_column(u'django_federal_reserve_data', 'start_date_inclusive')

        # Deleting field 'Data.end_date_inclusive'
        db.delete_column(u'django_federal_reserve_data', 'end_date_inclusive')


    models = {
        'django_federal_reserve.data': {
            'Meta': {'ordering': "('series', '-date')", 'unique_together': "(('series', 'date'),)", 'object_name': 'Data'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'end_date_inclusive': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': "orm['django_federal_reserve.Series']"}),
            'start_date_inclusive': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'django_federal_reserve.series': {
            'Meta': {'object_name': 'Series'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'date_is_start': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150', 'primary_key': 'True', 'db_index': 'True'}),
            'last_updated': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'max_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'min_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'seasonal_adjustment': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'units': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_federal_reserve']