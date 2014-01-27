from django.conf import settings
from django.contrib import admin

import models

view_link = None
#try:
from admin_steroids.utils import view_related_link
from admin_steroids.queryset import ApproxCountQuerySet
#except ImportError:
#    pass

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
        'active',
    )
    
    search_fields = (
        'id',
        'title',
    )
    
    list_filter = (
        'active',
        'frequency',
        'seasonal_adjustment',
        'units',
    )
    
    readonly_fields = (
        'min_date',
        'max_date',
        'data_link',
    )
    
    def queryset(self, *args, **kwargs):
        qs = super(SeriesAdmin, self).queryset(*args, **kwargs)
        qs = qs._clone(klass=ApproxCountQuerySet)
        return qs
    
    def data_link(self, obj=None):
        if not obj:
            return ''
        return view_related_link(obj, 'data')
    data_link.allow_tags = True
    data_link.short_description = 'data'
    
admin.site.register(models.Series, SeriesAdmin)

class DataAdmin(admin.ModelAdmin):
    
    list_display = (
        'series',
        'date',
        'value',
    )
    search_fields = (
    )
    
    list_filter = (
    )
    
    readonly_fields = (
    )
    
    raw_id_fields = (
        'series',
    )
    
    def queryset(self, *args, **kwargs):
        qs = super(DataAdmin, self).queryset(*args, **kwargs)
        qs = qs._clone(klass=ApproxCountQuerySet)
        return qs
    
admin.site.register(models.Data, DataAdmin)
