import csv
import os
import math
import urllib2
import shutil
import zipfile
import dateutil.parser
from datetime import date, timedelta

from django.db import models

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
                if i == 1 or not i % 100:
                    print '(%i of %i)' % (i, total)
                row = dict(
                    (
                        (k or '').strip().lower().replace(' ', '_'),
                        (v or '').strip()
                    )
                    for k,v in row.iteritems()
                )
                if not row.get('file'):
                    continue
                row['id'] = row['file'].split('\\')[-1].split('.')[0]
                del row['file']
                row['last_updated'] = dateutil.parser.parse(row['last_updated']) if row['last_updated'] else None
                #print row
                series, _ = Series.objects.get_or_create(id=row['id'], defaults=row)

            total = len(list(source.namelist()))
            i = 0
            for section_fn in source.namelist():
            #for section_fn in ['FRED2_csv_2/data/4/4BIGEURORECP.csv']:
                i += 1
                if i == 1 or not i % 100:
                    print '(%i of %i)' % (i, total)
                if not section_fn.endswith('.csv'):
                    continue
                lines = source.open(section_fn, 'r').readlines()
                series_id = section_fn.split('/')[-1].split('.')[0]
                #print len(lines)
                #print series_id
                try:
                    series = Series.objects.get(id=series_id)
                    #print section_fn
                except Series.DoesNotExist:
                    continue
                #print series
                last_data = None
                for row in csv.DictReader(source.open(section_fn, 'r')):
                    row['date'] = dateutil.parser.parse(row['DATE'])
                    row['date'] = date(row['date'].year, row['date'].month, row['date'].day)
                    del row['DATE']
                    try:
                        row['value'] = float(row['VALUE'])
                    except ValueError:
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
        else:
            #TODO:use API to download data for each series_id individually
            #e.g. http://api.stlouisfed.org/fred/series/observations?series_id=DEXUSEU&api_key=<api_key>
            todo 
        
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
        