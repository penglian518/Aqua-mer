from django.contrib import admin

# Register your models here.
from .models import CalcSolutionMasterSpecies, CalcSolutionSpecies, Refs

class CalcSolutionMasterSpeciesAdmin(admin.ModelAdmin):
    model = CalcSolutionMasterSpecies
    list_display = ('Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'Charge', 'PubChemID', 'IUPACName', 'SMILES', 'XYZ', 'Ref', 'CreatedDate', 'Note', 'Source')

class CalcSolutionSpeciesAdmin(admin.ModelAdmin):
    model = CalcSolutionSpecies
    list_display = ('Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                    'GammaA', 'GammaB', 'NoCheck', 'MoleBalance', 'Software', 'SoftwareVersion', 'Functional',
                    'BasisSet', 'SolvationModel', 'Ref', 'CreatedDate', 'Note')

class RefsAdmin(admin.ModelAdmin):
    model = Refs
    list_display = ('RefID', 'Reference')

admin.site.register(CalcSolutionMasterSpecies, CalcSolutionMasterSpeciesAdmin)
admin.site.register(CalcSolutionSpecies, CalcSolutionSpeciesAdmin)
admin.site.register(Refs, RefsAdmin)