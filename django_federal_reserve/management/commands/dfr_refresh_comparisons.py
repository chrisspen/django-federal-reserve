#!/usr/bin/env python
import sys
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from django_federal_reserve import models

class Command(BaseCommand):
    help = ''
    args = ''
    option_list = BaseCommand.option_list + (
        make_option('--config',
            help='Specific config to update.'),
        make_option('--other-series',
            help='Specific other series to update.'),
        make_option('--force',
            action='store_true',
            default=False,
            help='Ignores fresh flag.'),
#         make_option('--delete',
#             action='store_true',
#             default=False,
#             help='Ignores fresh flag.'),
    )
    
    def handle(self, *args, **options):
        settings.DEBUG = False
        force = options['force']
#         delete = options['delete']
        config = options['config']
        other_series = options['other_series']
        qs = models.ComparisonConfig.objects.all()
        if not force:
            qs = qs.filter(fresh=False)
        if config:
            qs = qs.filter(id=int(config))
        print '%i configs found' % qs.count()
        for cc in qs.iterator():
            cc.populate(force=force)
            
            qs2 = cc.comparisons.all()
            if not force:
                qs2 = qs2.filter(fresh=False)
            else:
                qs2.update(correlation=None)
            if other_series:
                qs2 = qs2.filter(series__id=other_series)
            print '%i comparisons found' % qs2.count()
            total = qs2.count()
            i = 0
            for r in qs2.iterator():
                i += 1
                print '\r%i of %i %.02f%%' % (i, total, i/float(total)*100),
                sys.stdout.flush()
                r.calculate()
                
            cc.save()
            print
            