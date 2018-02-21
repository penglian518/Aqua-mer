from django.contrib import admin

# Register your models here.

from .models import HgSpeciJob, SPElements

class SPElementsInline(admin.TabularInline):
    model = SPElements
    extra = 1

class HgSpeciJobAdmin(admin.ModelAdmin):
    model = HgSpeciJob

    inlines = [SPElementsInline, ]

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SPUnit', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease')


class SPElementsAdmin(admin.ModelAdmin):
    model = SPElements

    list_display = ('JobID', 'Element', 'Concentration', 'PE', 'PPB', 'PPBFormula', )



admin.site.register(HgSpeciJob, HgSpeciJobAdmin)
admin.site.register(SPElements, SPElementsAdmin)
