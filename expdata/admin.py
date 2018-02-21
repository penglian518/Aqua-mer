from django.contrib import admin

# Register your models here.

from .models import Compound, PKA, StabilityConstants, dGsolv, Refs, Electrolyte, Reactants



class PKAInline(admin.TabularInline):
    model = PKA
    extra = 1

class StabilityConstantsInline(admin.TabularInline):
    model = StabilityConstants
    extra = 1

class dGsolvInline(admin.TabularInline):
    model = dGsolv
    extra = 1



class CompoundAdmin(admin.ModelAdmin):
    model = Compound

    #fields = ['PubChemID', 'Formula', 'InChIKey']
    inlines = [dGsolvInline, PKAInline, StabilityConstantsInline, ]

    def get_pKa(self, obj):
        return obj.PKa.pKa
    get_pKa.short_description = 'pKa'
    get_pKa.admin_order_field = 'PKA__pKa'

    list_display = ('id', 'PubChemID', 'Name', 'Formula', 'MolecularWeight', 'Charge', 'InChIKey',)

class PKAAdmin(admin.ModelAdmin):
    model = PKA
    list_display = ('MolID', 'H', 'L', 'IonicStrength', 'Electrolyte', 'TemperatureC', 'pKa', 'pKaReference',
                    'dHr', 'dSr', 'dGr', 'ThermalReference',)

class StabilityConstantsAdmin(admin.ModelAdmin):
    model = StabilityConstants
    list_display = ('MolID', 'Metal', 'Constant', 'M', 'L', 'H', 'OH', 'Lprime', 'LprimeNumber', 'Reactants', 'IonicStrength',
                    'Electrolyte', 'TemperatureC', 'LogBorK', 'dHr', 'dSr', 'dGr', 'ThermalReference',)

class dGsolvAdmin(admin.ModelAdmin):
    model = dGsolv
    list_display = ('MolID', 'dGsolv')

class RefsAdmin(admin.ModelAdmin):
    model = Refs
    list_display = ('RefID', 'Reference')

class ElectrolyteAdmin(admin.ModelAdmin):
    model = Electrolyte
    list_display = ('Electrolyte', )

class ReactantsAdmin(admin.ModelAdmin):
    model = Reactants
    list_display = ('Reactants', )

admin.site.register(Compound, CompoundAdmin)
#admin.site.register(PKA, PKAAdmin)
#admin.site.register(StabilityConstants, StabilityConstantsAdmin)
#admin.site.register(dGsolv, dGsolvAdmin)
admin.site.register(Refs, RefsAdmin)
admin.site.register(Electrolyte, ElectrolyteAdmin)
admin.site.register(Reactants, ReactantsAdmin)

