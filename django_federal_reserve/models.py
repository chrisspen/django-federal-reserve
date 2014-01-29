import csv
import dateutil.parser
import gc
import math
import os
import shutil
import sys
import urllib2
import zipfile
from datetime import date, timedelta

import django
from django.db import models
from django.db.models import Max, Min, Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone

import fred

from django_data_mirror.models import DataSource, DataSourceControl, DataSourceFile, register

import constants as c
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
    
    def download_bulk_data(self, fn=None, no_download=False):
        """
        Downloads bulk CSV data for initial database population.
        """
        tmp_local_fn = '/tmp/_%s' % (s.BULK_URL.split('/')[-1],)
        local_fn = fn or ('/tmp/%s' % (s.BULK_URL.split('/')[-1],))
        source = DataSourceControl.objects.get(slug=type(self).__name__)
        dsfile, _ = DataSourceFile.objects.get_or_create(source=source, name=local_fn)
        django.db.transaction.commit()
        if dsfile.complete:
            return local_fn
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
            DataSourceFile.objects.filter(id=dsfile.id).update(downloaded=True)
        return local_fn
    
    def refresh(self, bulk=False, skip_to=None, fn=None, no_download=False, **kwargs):
        """
        Reads the associated API and saves data to tables.
        """
        
        if skip_to:
            skip_to = int(skip_to)
        
        tmp_debug = settings.DEBUG
        settings.DEBUG = False
        django.db.transaction.enter_transaction_management()
        django.db.transaction.managed(True)
        
        try:
            if bulk:
                local_fn = self.download_bulk_data(fn=fn, no_download=no_download)
                dsfile, _ = DataSourceFile.objects.get_or_create(name=local_fn)
                if dsfile.complete:
                    return
                
                # Process CSV.
                print 'Reading file...'
                sys.stdout.flush()
                source = zipfile.ZipFile(local_fn, 'r')
                if dsfile.total_lines_complete:
                    total = dsfile.total_lines
                    if not skip_to:
                        skip_to = dsfile.total_lines_complete
                else:
                    total = len(source.open(s.BULK_INDEX_FN, 'r').readlines())
                    DataSourceFile.objects.filter(id=dsfile.id).update(
                        complete=False,
                        total_lines=total,
                        total_lines_complete=0,
                        percent=0,
                    )
                django.db.transaction.commit()
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
                just_skipped = False
                data = csv.DictReader(line_iter, delimiter=';')
                for row in data:
                    i += 1
                    if skip_to and i < skip_to:
                        if not just_skipped:
                            print
                        print '\rSkipping from %s to %s...' % (i, skip_to),
                        sys.stdout.flush()
                        just_skipped = True
                        continue
                    elif just_skipped:
                        just_skipped = False
                        print
                        
                    DataSourceFile.objects.filter(id=dsfile.id).update(
                        downloaded=True,
                        complete=False,
                        total_lines=total,
                        total_lines_complete=i,
                        percent=i/float(total)*100,
                    )
                    if not i % 10:
                        django.db.transaction.commit()
                        
                    row = dict(
                        (
                            (k or '').strip().lower().replace(' ', '_'),
                            (v or '').strip()
                        )
                        for k,v in row.iteritems()
                    )
                    if not row.get('file'):
                        continue
                    print '\rLoading %s %.02f%% (%i of %i)...' % (row.get('file'), i/float(total)*100, i, total),
                    sys.stdout.flush()
                    row['id'] = row['file'].split('\\')[-1].split('.')[0]
                    section_fn = row['file'] # FRED2_csv_2/data/4/4BIGEURORECP.csv
                    del row['file']
                    if row['last_updated']:
                        row['last_updated'] = dateutil.parser.parse(row['last_updated'])
                        row['last_updated'] = date(row['last_updated'].year, row['last_updated'].month, row['last_updated'].day)
                    #print row
                    series, _ = Series.objects.get_or_create(id=row['id'], defaults=row)
                    series.last_updated = row['last_updated']
                    series_min_date = series.min_date
                    series_max_date = series.max_date
                    prior_series_dates = set(series.data.all().values_list('date', flat=True))
                    
                    if series.max_date and series.last_updated > (series.max_date - timedelta(days=s.LAST_UPDATE_DAYS)):
                        continue
                    elif not section_fn.endswith('.csv'):
                        continue
                    
                    section_fn = 'FRED2_csv_2/data/' + section_fn.replace('\\', '/')
                    #print 'section_fn:',section_fn
                    lines = source.open(section_fn, 'r').readlines()
                    #last_data = None
                    last_data_date = None
                    last_data_value = None
                    total2 = len(source.open(section_fn, 'r').readlines())
                    i2 = 0
                    if s.EXPAND_DATA_TO_DAYS:
                        print
                    series_data_pending = []
                    for row in csv.DictReader(source.open(section_fn, 'r')):
                        i2 += 1
                        if s.EXPAND_DATA_TO_DAYS:
                            print '\r\tLine %.02f%% (%i of %i)' % (i2/float(total2)*100, i2, total2),
                        sys.stdout.flush()
                        row['date'] = dateutil.parser.parse(row['DATE'])
                        row['date'] = date(row['date'].year, row['date'].month, row['date'].day)
                        
#                        series_min_date = min(series_min_date or row['date'], row['date'])
#                        series_max_date = max(series_max_date or row['date'], row['date'])
                        
                        del row['DATE']
                        try:
                            row['value'] = float(row['VALUE'])
                        except ValueError:
                            print
                            print 'Invalid value: "%s"' % (row['VALUE'],)
                            sys.stdout.flush()
                            continue
                        del row['VALUE']
                        #print row
                        
                        if s.EXPAND_DATA_TO_DAYS and last_data_date:
                            intermediate_days = (row['date'] - last_data_date).days
                            #print 'Expanding data to %i intermediate days...' % (intermediate_days,)
                            #sys.stdout.flush()
                            #Data.objects.bulk_create([
                            series_data_pending.extend([
                                Data(series=series, date=last_data_date+timedelta(days=_days), value=last_data_value)
                                for _days in xrange(1, intermediate_days)
                                if (last_data_date+timedelta(days=_days)) not in prior_series_dates
                            ])
                        
                        #data, _ = Data.objects.get_or_create(series=series, date=row['date'], defaults=row)
                        if row['date'] not in prior_series_dates:
                            data = Data(series=series, date=row['date'], value=row['value'])
                            series_data_pending.append(data)
                        #data.save()
                        last_data_date = row['date']
                        last_data_value = row['value']
                    if series_data_pending:
                        Data.objects.bulk_create(series_data_pending)
#                    print '\r\tLine %.02f%% (%i of %i)' % (100, i2, total2),
#                    print
                    series.save()
                        
                    # Cleanup.
                    django.db.transaction.commit()
                    Series.objects.update()
                    Data.objects.update()
                    gc.collect()
                    
                DataSourceFile.objects.filter(id=dsfile.id).update(
                    complete=True,
                    downloaded=True,
                    total_lines=total,
                    total_lines_complete=total,
                    percent=100,
                )
                    
            else:
                #TODO:use API to download data for each series_id individually
                #e.g. http://api.stlouisfed.org/fred/series/observations?series_id=DEXUSEU&api_key=<api_key>
                #TODO:check for revised values using output_type?
                #http://api.stlouisfed.org/docs/fred/series_observations.html#output_type
                q = Series.objects.get_stale()
                fred.key(s.API_KEY)
                i = 0
                total = q.count()
                print '%i stale series found.' % (total,)
                for series in q.iterator():
                    i += 1
                    print '%i of %i' % (i, total)
                    sys.stdout.flush()
                    observation_start = None
                    if series.max_date:
                        observation_start = series.max_date - timedelta(days=7)
                    series_data = fred.observations(
                        series.id,
                        observation_start=observation_start)
                    for data in series_data['observations']:
                        print series, data['date'], data['value']
                        value = float(data['value'])
                        data, created = Data.objects.get_or_create(
                            series=series,
                            date=data['date'],
                            defaults=dict(value=value))
                        if not created:
                            data.value = value
                            data.save()
                    django.db.transaction.commit()
                
        finally:
            #print "Committing..."
            settings.DEBUG = tmp_debug
            django.db.transaction.commit()
            django.db.transaction.leave_transaction_management()
            #django.db.connection.close()
            #print "Committed."
        
    def get_feeds(self, bulk=False):
        return []

register(FederalReserveDataSource)

class SeriesManager(models.Manager):
    
    def get_stale(self, enabled=True):
        q = self.all()
        q = q.filter(active=True)
        if enabled is not None:
            q = q.filter(enabled=enabled)
        q = q.filter(
            Q(max_date__isnull=True)|\
            Q(frequency__startswith=c.ANNUALLY, max_date__lte=timezone.now()-timedelta(days=365))|\
            Q(frequency__startswith=c.QUARTERLY, max_date__lte=timezone.now()-timedelta(days=90))|\
            Q(frequency__startswith=c.MONTHLY, max_date__lte=timezone.now()-timedelta(days=30))|\
            Q(frequency__startswith=c.DAILY, max_date__lte=timezone.now()-timedelta(days=1))
        )
        return q

class Series(models.Model):
    
    objects = SeriesManager()
    
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
        help_text=_('''NSA=not seasonally adjusted, SA=seasonally adjusted,
SAAR=seasonally adjusted annual rates, SSA=smoothed seasonally adjusted''')
    )
    
    last_updated = models.DateField(
        blank=True,
        null=True,
        db_index=True,
    )
    
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_('''If checked, indicates this series is still being updated
            by the Fed.'''))
    
    enabled = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='load',
        help_text=_('''If checked, data will be downloaded for this series.'''))
    
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
    
    def fresh(self):
        return not type(self).objects.get_stale(enabled=None).filter(id=self.id).exists()
    fresh.boolean = True
    
    def save(self, *args, **kwargs):
        
        if 'discontinued' in (self.title or '').lower():
            self.active = False
        
        if self.id:
            if not self.min_date:
                self.min_date = self.data.all().aggregate(Min('date'))['date__min']
            if not self.max_date:
                self.max_date = self.data.all().aggregate(Max('date'))['date__max']
        
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
        