# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Series.min_date'
        db.add_column(u'django_federal_reserve_series', 'min_date',
                      self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Series.max_date'
        db.add_column(u'django_federal_reserve_series', 'max_date',
                      self.gf('django.db.models.fields.DateField')(db_index=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Series.min_date'
        db.delete_column(u'django_federal_reserve_series', 'min_date')

        # Deleting field 'Series.max_date'
        db.delete_column(u'django_federal_reserve_series', 'max_date')


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
            'max_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'min_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'seasonal_adjustment': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'units': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['django_federal_reserve']