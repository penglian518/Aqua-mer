from django.contrib import admin

# Register your models here.

from .models import HgSpeciJob, SPElements, SPMasterSpecies, SPSolutionSpecies

class SPElementsInline(admin.TabularInline):
    model = SPElements
    extra = 1

class SPMasterSpeciesInline(admin.TabularInline):
    model = SPMasterSpecies
    extra = 1

class SPSolutionSpeciesInline(admin.TabularInline):
    model = SPSolutionSpecies
    extra = 1



class HgSpeciJobAdmin(admin.ModelAdmin):
    model = HgSpeciJob
    inlines = [SPElementsInline,
               SPMasterSpeciesInline,
               SPSolutionSpeciesInline
               ]
    list_display = ('id', 'JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SPUnit', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease', 'SPRedoxMethod', 'SPRedoxValue',
                    'SPDensity', 'SPTitrant', 'SPTitrantConcentration', 'SPDBtoUse', 'SPUserDefinedInput', 'SPpe', 'SPRedox')

class SPElementsAdmin(admin.ModelAdmin):
    model = SPElements
    list_display = ('SPJobID', 'JobID', 'Element', 'Concentration', 'Unit', 'AS', 'ASFormula', 'GFW', 'GFWFormula', 'Redox',)

class SPMasterSpeciesAdmin(admin.ModelAdmin):
    model = SPMasterSpecies
    list_display = ('SPJobID', 'JobID', 'Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'Note',)

class SPSolutionSpeciesAdmin(admin.ModelAdmin):
    model = SPSolutionSpecies
    list_display = ('SPJobID', 'JobID', 'Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5', 'AEA6',
                    'DW1', 'DW2', 'DW3', 'DW4', 'VM1', 'VM2', 'VM3', 'VM4', 'VM5', 'VM6', 'VM7', 'VM8', 'VM9', 'VM10',
                    'GammaA', 'GammaB', 'NoCheck', 'MoleBalance', 'Note',)



admin.site.register(HgSpeciJob, HgSpeciJobAdmin)
admin.site.register(SPElements, SPElementsAdmin)
admin.site.register(SPMasterSpecies, SPMasterSpeciesAdmin)
admin.site.register(SPSolutionSpecies, SPSolutionSpeciesAdmin)
