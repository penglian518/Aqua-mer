from django.contrib import admin

# Register your models here.
from .models import SolutionMasterSpecies, SolutionSpecies, Phases, SurfaceMasterSpecies, SurfaceSpecies,\
                    ExchangeMasterSpecies, ExchangeSpecies, Rates, Refs

class SolutionMasterSpeciesAdmin(admin.ModelAdmin):
    model = SolutionMasterSpecies
    list_display = ('Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'Ref', 'CreatedDate', 'Note')

class SolutionSpeciesAdmin(admin.ModelAdmin):
    model = SolutionSpecies
    list_display = ('Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                    'GammaA', 'GammaB', 'NoCheck', 'MoleBalance', 'Ref', 'CreatedDate', 'Note')

class PhasesAdmin(admin.ModelAdmin):
    model = Phases
    list_display = ('PhaseName', 'Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                     'Ref', 'CreatedDate', 'Note')

class SurfaceMasterSpeciesAdmin(admin.ModelAdmin):
    model = SurfaceMasterSpecies
    list_display = ('BindingSite', 'SurfaceMaster', 'Ref', 'CreatedDate', 'Note')

class SurfaceSpeciesAdmin(admin.ModelAdmin):
    model = SurfaceSpecies
    list_display = ('Reaction', 'LogK', 'Ref', 'CreatedDate', 'Note')

class ExchangeMasterSpeciesAdmin(admin.ModelAdmin):
    model = ExchangeMasterSpecies
    list_display = ('ExchangeName', 'ExchangeMaster', 'Ref', 'CreatedDate', 'Note')

class ExchangeSpeciesAdmin(admin.ModelAdmin):
    model = ExchangeSpecies
    list_display = ('Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'GammaA', 'GammaB', 'Davies', 'Ref', 'CreatedDate', 'Note')

class RatesAdmin(admin.ModelAdmin):
    model = Rates
    list_display = ('Name', 'BasicStatement', 'Ref', 'CreatedDate', 'Note')

class RefsAdmin(admin.ModelAdmin):
    model = Refs
    list_display = ('RefID', 'Reference')


admin.site.register(SolutionMasterSpecies, SolutionMasterSpeciesAdmin)
admin.site.register(SolutionSpecies, SolutionSpeciesAdmin)
admin.site.register(Phases, PhasesAdmin)
admin.site.register(SurfaceMasterSpecies, SurfaceMasterSpeciesAdmin)
admin.site.register(SurfaceSpecies, SurfaceSpeciesAdmin)
admin.site.register(ExchangeMasterSpecies, ExchangeMasterSpeciesAdmin)
admin.site.register(ExchangeSpecies, ExchangeSpeciesAdmin)
admin.site.register(Rates, RatesAdmin)
admin.site.register(Refs, RefsAdmin)

