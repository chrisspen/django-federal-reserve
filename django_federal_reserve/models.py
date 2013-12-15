import csv
import gc
import os
import math
import urllib2
import shutil
import zipfile
import dateutil.parser
from datetime import date, timedelta

import django
from django.db import models
from django.conf import settings

from django_data_mirror.models import DataSource, ForeignKey

import settings as s

try:
    from admin_steroids.utils import StringWithTitle
    APP_LABEL = StringWithTitle('django_federal_reserve', 'Federal Reserve')
except ImportError:
    APP_LABEL = 'django_federal_reserve'

class FederalReserveDataSource(DataSource):
    """
    Generate or update the schema code by running:
        ./manage.py data_mirror_analyze FederalReserveDataSource
    """
    
    @classmethod
    def download_bulk_data(self, fn=None, no_download=False):
        """
        Downloads bulk CSV data for initial database population.
        """
        tmp_local_fn = '/tmp/_%s' % (s.BULK_URL.split('/')[-1],)
        local_fn = fn or ('/tmp/%s' % (s.BULK_URL.split('/')[-1],))
        if os.path.isfile(local_fn):
            print 'File %s already downloaded.' % (local_fn,)
        elif no_download:
            raise Exception, 'File %s does not exist.' % fn
        else:
            url = s.BULK_URL
            print 'Downloading %s...' % (url,)
#            opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
#            opener.open(url)
#            return

#            req = urllib2.urlopen(url)
#            with open(tmp_local_fn, 'wb') as fp:
#                shutil.copyfileobj(req, fp, CHUNK)
#            print 'Saving complete file...'
#            os.rename(tmp_local_fn, local_fn)
            os.system('cd /tmp; wget %s' % (url,))
            
            # Show download progress.
            #TODO:fix? response doesn't include Content-Length
#            req = urllib2.urlopen(url)
#            #print 'headers:',req.info().headers
#            #return
#            total_size = int(req.info().getheader('Content-Length').strip())
#            downloaded = 0
#            with open(tmp_local_fn, 'wb') as fp:
#                while True:
#                    chunk = req.read(CHUNK)
#                    downloaded += len(chunk)
#                    print '%.02f%%' % (math.floor((downloaded / total_size) * 100),)
#                    if not chunk: break
#                    fp.write(chunk)
            print 'Downloaded %s successfully.' % (local_fn,)
        return local_fn
    
    @classmethod
    def refresh(cls, bulk=False, fn=None, no_download=False, **kwargs):
        """
        Reads the associated API and saves data to tables.
        """
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        
        try:
                
            if bulk:
                local_fn = cls.download_bulk_data(fn=fn, no_download=no_download)
                # Process CSV.
                print 'Reading file...'
                source = zipfile.ZipFile(local_fn, 'r')
                total = len(source.open(s.BULK_INDEX_FN, 'r').readlines())
                line_iter = iter(source.open(s.BULK_INDEX_FN, 'r'))
                offset = 0
                while 1:
                    try:
                        line = line_iter.next()
                        offset += 1
                        #print 'line:',line.strip()
                        if line.lower().startswith('series '):
                            line_iter.next()
                            offset += 1
                            break
                    except StopIteration:
                        break
                total -= offset
                i = 0
                data = csv.DictReader(line_iter, delimiter=';')
                for row in data:
                    i += 1
                    row = dict(
                        (
                            (k or '').strip().lower().replace(' ', '_'),
                            (v or '').strip()
                        )
                        for k,v in row.iteritems()
                    )
                    if not row.get('file'):
                        continue
                    print 'Loading %s %.02f%% (%i of %i)...' % (row.get('file'), i/float(total)*100, i, total)
                    row['id'] = row['file'].split('\\')[-1].split('.')[0]
                    section_fn = row['file'] # FRED2_csv_2/data/4/4BIGEURORECP.csv
                    del row['file']
                    row['last_updated'] = dateutil.parser.parse(row['last_updated']) if row['last_updated'] else None
                    #print row
                    series, _ = Series.objects.get_or_create(id=row['id'], defaults=row)
                    
                    if series.max_date and series.last_updated > (series.max_date - timedelta(days=30)):
                        continue
                    elif not section_fn.endswith('.csv'):
                        continue
                    
                    section_fn = 'FRED2_csv_2/data/' + section_fn.replace('\\', '/')
                    #print 'section_fn:',section_fn
                    lines = source.open(section_fn, 'r').readlines()
                    last_data = None
                    total2 = len(source.open(section_fn, 'r').readlines())
                    i2 = 0
                    for row in csv.DictReader(source.open(section_fn, 'r')):
                        i2 += 1
                        print '\r\tLine %.02f%% (%i of %i)' % (i2/float(total2)*100, i2, total2),
                        row['date'] = dateutil.parser.parse(row['DATE'])
                        row['date'] = date(row['date'].year, row['date'].month, row['date'].day)
                        del row['DATE']
                        try:
                            row['value'] = float(row['VALUE'])
                        except ValueError:
                            print
                            print 'Invalid value: "%s"' % (row['VALUE'],)
                            continue
                        del row['VALUE']
                        #print row
                        
                        if s.EXPAND_DATA_TO_DAYS and last_data:
                            while row['date'] > last_data.date:
                                last_data.date += timedelta(days=1)
                                Data.objects.get_or_create(
                                    series=series,
                                    date=last_data.date,
                                    defaults=dict(value=last_data.value),
                                )
                        
                        data, _ = Data.objects.get_or_create(series=series, date=row['date'], defaults=row)
                        data.value = row['value']
                        data.save()
                        last_data = data
                    print
                        
                    # Cleanup.
                    django.db.transaction.commit()
                    Series.objects.update()
                    Data.objects.update()
                    gc.collect()
                    
            else:
                #TODO:use API to download data for each series_id individually
                #e.g. http://api.stlouisfed.org/fred/series/observations?series_id=DEXUSEU&api_key=<api_key>
                todo
                
        finally:
            print "Committing..."
            settings.DEBUG = tmp_debug
            django.db.transaction.commit()
            django.db.transaction.leave_transaction_management()
            django.db.connection.close()
            print "Committed."
        
    @classmethod
    def get_feeds(cls, bulk=False):
        return []

class Series(models.Model):
    
    id = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        primary_key=True,
        unique=True,
        db_index=True,
    )
    
    title = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    
    units = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
    )
    
    frequency = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
    )
    
    seasonal_adjustment = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
    )
    
    last_updated = models.DateField(
        blank=True,
        null=True,
        db_index=True,
    )
    
    active = models.BooleanField(default=True)
    
    min_date = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        editable=False,
    )
    
    max_date = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        editable=False,
    )
    
    class Meta:
        verbose_name_plural = 'series'
        app_label = APP_LABEL
        #db_table = 'federal_reserve_series'#TODO:ignored by south?!
    
    def __unicode__(self):
        #return u'<%s: %s>' % (type(self).__name__, self.id)
        return self.id
    
    def __repr__(self):
        return unicode(self)
    
    def save(self, *args, **kwargs):
        
        if 'discontinued' in (self.title or '').lower():
            self.active = False
        
        super(Series, self).save(*args, **kwargs)

class Data(models.Model):
    
    series = models.ForeignKey('Series', related_name='data')
    
    date = models.DateField(
        blank=False,
        null=False,
        db_index=True,
    )
    
    value = models.FloatField(
        blank=False,
        null=False,
    )
    
    class Meta:
        verbose_name_plural = 'data'
        app_label = APP_LABEL
        #db_table = 'federal_reserve_data'#TODO:ignored by south?!
        unique_together = (
            ('series', 'date'),
        )
        ordering = ('series', '-date')
        
    def save(self, *args, **kwargs):
        super(Data, self).save(*args, **kwargs)
        self.series.min_date = min(self.series.min_date or self.date, self.date)
        self.series.max_date = max(self.series.max_date or self.date, self.date)
        self.series.save()
        