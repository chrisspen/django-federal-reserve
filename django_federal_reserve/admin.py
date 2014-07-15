from django.conf import settings
from django.contrib import admin
from django.contrib.admin import FieldListFilter, ListFilter, SimpleListFilter
from django.utils.translation import ugettext, ugettext_lazy as _

import models

from admin_steroids.utils import view_related_link
from admin_steroids.queryset import ApproxCountQuerySet

class FreshListFilter(SimpleListFilter):
    
    title = 'Freshness'
    
    parameter_name = 'freshness'
    
    default_value = None
    
    def __init__(self, request, params, model, model_admin):
        self.parameter_val = None
        try:
            self.parameter_val = request.GET.get(self.parameter_name, self.default_value)
            if self.parameter_val is not None:
                if self.parameter_val in (True, 'True', 1, '1'):
                    self.parameter_val = True
                else:
                    self.parameter_val = False
        except Exception, e:
            pass
        super(FreshListFilter, self).__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        """
        Must be overriden to return a list of tuples (value, verbose value)
        """
        return [
            (None, _('All')),
            (True, _('Fresh')),
            (False, _('Stale')),
        ]

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.parameter_val == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset.
        """
        if self.parameter_val is not None:
            if self.parameter_val:
                #TODO:fix, bad unusable performance?
                queryset = models.Series.objects.get_fresh(q=queryset)
            else:
                #queryset = queryset.filter(id__in=models.Series.objects.get_stale().values_list('id', flat=True))
                queryset = models.Series.objects.get_stale(q=queryset)
        return queryset

class SeriesAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'title',
        'units',
        'frequency',
        'seasonal_adjustment',
        'last_updated',
        'min_date',
        'max_date',
        'popularity',
        'active',
        'enabled',
        'fresh',
        'date_is_start',
    )
    
    search_fields = (
        'id',
        'title',
    )
    
    list_filter = (
        FreshListFilter,
        'active',
        'enabled',
        'date_is_start',
        'frequency',
        'seasonal_adjustment',
        'units',
    )
    
    readonly_fields = (
        'id',
        'fred_link',
        'title',
        'frequency',
        'seasonal_adjustment',
        'last_updated',
        'popularity',
        'min_date',
        'max_date',
        'data_link',
        'fresh',
        'units',
        'date_is_start',
    )
    
    actions = (
        'enable_load',
        'disable_load',
    )
    
    fieldsets = (
        (None, {
            'fields': (
                'id',
                'title',
                'data_link',
                'fred_link',
            )
        }),
        ('Flags', {
            'fields': (
                'active',
                'enabled',
                'fresh',
                'date_is_start',
            )
        }),
        ('Details', {
            'fields': (
                'frequency',
                'seasonal_adjustment',
                'units',
                'last_updated',
                'popularity',
                'min_date',
                'max_date',
            )
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def queryset(self, *args, **kwargs):
        qs = super(SeriesAdmin, self).queryset(*args, **kwargs)
        qs = qs._clone(klass=ApproxCountQuerySet)
        return qs
    
    def fred_link(self, obj=None):
        if not obj:
            return ''
        url = 'http://research.stlouisfed.org/fred2/series/%s' % obj.id
        return '<a href="%s" target="_blank" class="button">View</a>' % (url,)
    fred_link.allow_tags = True
    fred_link.short_description = 'FRED'
    
    def data_link(self, obj=None):
        if not obj:
            return ''
        return view_related_link(obj, 'data')
    data_link.allow_tags = True
    data_link.short_description = 'data'
    
    def enable_load(self, request, queryset):
        models.Series.objects.filter(id__in=queryset).update(enabled=True)
    enable_load.short_description = 'Enable value loading of selected %(verbose_name_plural)s'
    
    def disable_load(self, request, queryset):
        models.Series.objects.filter(id__in=queryset).update(enabled=False)
    disable_load.short_description = 'Disable value loading of selected %(verbose_name_plural)s'
    
admin.site.register(models.Series, SeriesAdmin)

class DataAdmin(admin.ModelAdmin):
    
    list_display = (
        'series',
        'date',
        'start_date_inclusive',
        'end_date_inclusive',
        'value',
    )
    search_fields = (
    )
    
    list_filter = (
    )
    
    readonly_fields = (
        'series',
        'date',
        'start_date_inclusive',
        'end_date_inclusive',
        'value',
    )
    
    raw_id_fields = (
        'series',
    )
    
    def has_add_permission(self, request):
        return False
    
    def queryset(self, *args, **kwargs):
        qs = super(DataAdmin, self).queryset(*args, **kwargs)
        qs = qs._clone(klass=ApproxCountQuerySet)
        return qs
    
admin.site.register(models.Data, DataAdmin)
