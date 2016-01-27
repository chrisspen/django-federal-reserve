# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ComparisonConfig.fresh'
        db.add_column(u'django_federal_reserve_comparisonconfig', 'fresh',
                      self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ComparisonConfig.fresh'
        db.delete_column(u'django_federal_reserve_comparisonconfig', 'fresh')


    models = {
        u'django_federal_reserve.comparison': {
            'Meta': {'object_name': 'Comparison'},
            'config': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparisons'", 'to': u"orm['django_federal_reserve.ComparisonConfig']"}),
            'correlation': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fresh': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparisons'", 'to': "orm['django_federal_reserve.Series']"})
        },
        u'django_federal_reserve.comparisonconfig': {
            'Meta': {'object_name': 'ComparisonConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'fresh': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'other_filter': ('django.db.models.fields.CharField', [], {'default': "'one-day-diff-bool'", 'max_length': '50'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comparison_configs'", 'to': "orm['django_federal_reserve.Series']"})
        },
        'django_federal_reserve.data': {
            'Meta': {'ordering': "('series', '-date')", 'unique_together': "(('series', 'date'),)", 'object_name': 'Data', 'index_together': "(('series', 'date'), ('series', 'end_date_inclusive'), ('series', 'start_date_inclusive', 'end_date_inclusive'))"},
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