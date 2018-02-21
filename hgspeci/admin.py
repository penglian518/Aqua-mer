from django.contrib import admin

# Register your models here.

from .models import HgSpeciJob, SPElements, SPMasterSpecies

class SPElementsInline(admin.TabularInline):
    model = SPElements
    extra = 1

class SPMasterSpeciesInline(admin.TabularInline):
    model = SPMasterSpecies
    extra = 1

class HgSpeciJobAdmin(admin.ModelAdmin):
    model = HgSpeciJob
    inlines = [SPElementsInline, SPMasterSpeciesInline]
    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SPUnit', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease')


class SPElementsAdmin(admin.ModelAdmin):
    model = SPElements
    list_display = ('JobID', 'Element', 'Concentration', 'PE', 'PPB', 'PPBFormula', )

class SPMasterSpeciesAdmin(admin.ModelAdmin):
    model = SPMasterSpecies
    list_display = ('JobID', 'Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'Note',)



admin.site.register(HgSpeciJob, HgSpeciJobAdmin)
admin.site.register(SPElements, SPElementsAdmin)
admin.site.register(SPMasterSpecies, SPMasterSpeciesAdmin)
