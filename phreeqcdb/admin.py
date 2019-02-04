from django.contrib import admin

# Register your models here.
from .models import SolutionMasterSpecies, SolutionSpecies, Phases, SurfaceMasterSpecies, SurfaceSpecies,\
                    ExchangeMasterSpecies, ExchangeSpecies, Rates, Refs, DBSources

class SolutionMasterSpeciesAdmin(admin.ModelAdmin):
    model = SolutionMasterSpecies
    list_display = ('Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class SolutionSpeciesAdmin(admin.ModelAdmin):
    model = SolutionSpecies
    list_display = ('Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                    'DW1', 'DW2', 'DW3', 'DW4', 'VM1', 'VM2', 'VM3', 'VM4', 'VM5', 'VM6', 'VM7', 'VM8', 'VM9', 'VM10',
                    'GammaA', 'GammaB', 'NoCheck', 'MoleBalance', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class PhasesAdmin(admin.ModelAdmin):
    model = Phases
    list_display = ('PhaseName', 'Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                    'TC', 'PC', 'OMEGA', 'VM1', 'VM2', 'VM3', 'VM4', 'VM5', 'VM6', 'VM7', 'VM8', 'VM9', 'VM10',
                    'DBSource', 'Ref', 'CreatedDate', 'Note')

class SurfaceMasterSpeciesAdmin(admin.ModelAdmin):
    model = SurfaceMasterSpecies
    list_display = ('BindingSite', 'SurfaceMaster', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class SurfaceSpeciesAdmin(admin.ModelAdmin):
    model = SurfaceSpecies
    list_display = ('Reaction', 'LogK', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class ExchangeMasterSpeciesAdmin(admin.ModelAdmin):
    model = ExchangeMasterSpecies
    list_display = ('ExchangeName', 'ExchangeMaster', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class ExchangeSpeciesAdmin(admin.ModelAdmin):
    model = ExchangeSpecies
    list_display = ('Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'GammaA', 'GammaB', 'Davies', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class RatesAdmin(admin.ModelAdmin):
    model = Rates
    list_display = ('Name', 'BasicStatement', 'DBSource', 'Ref', 'CreatedDate', 'Note')

class RefsAdmin(admin.ModelAdmin):
    model = Refs
    list_display = ('id', 'RefID', 'Reference')

class DBSourceAdmin(admin.ModelAdmin):
    model = DBSources
    list_display = ('id', 'DBID', 'DBNote')


admin.site.register(SolutionMasterSpecies, SolutionMasterSpeciesAdmin)
admin.site.register(SolutionSpecies, SolutionSpeciesAdmin)
admin.site.register(Phases, PhasesAdmin)
admin.site.register(SurfaceMasterSpecies, SurfaceMasterSpeciesAdmin)
admin.site.register(SurfaceSpecies, SurfaceSpeciesAdmin)
admin.site.register(ExchangeMasterSpecies, ExchangeMasterSpeciesAdmin)
admin.site.register(ExchangeSpecies, ExchangeSpeciesAdmin)
admin.site.register(Rates, RatesAdmin)
admin.site.register(Refs, RefsAdmin)
admin.site.register(DBSources, DBSourceAdmin)

