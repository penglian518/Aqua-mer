from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm, Textarea

from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _


# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class SolutionMasterSpecies(models.Model):
    Element = models.CharField(max_length=50, blank=True, default='')
    Species = models.CharField(max_length=50, blank=True, default='')
    Alkalinity = models.FloatField(blank=True, default=0.0)
    GFWorFormula = models.CharField(max_length=50, blank=True, default='0.0')
    GFWforElement = models.FloatField(blank=True, null=True)

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Element)

@python_2_unicode_compatible  # only if you need to support Python 2
class SolutionSpecies(models.Model):
    Units = (
        ('kJ/mol', 'kJ'),
        ('kcal/mol', 'kcal'),
        ('J/mol', 'J'),
        ('cal/mol', 'cal'),
    )
    Reaction = models.CharField(max_length=200, blank=True, default='')
    LogK = models.FloatField(blank=True, default=0.0)
    DeltaH = models.FloatField(blank=True, default=0.0)
    DeltaHUnits = models.CharField(choices=Units, max_length=10, default='kJ/mol')
    AEA1 = models.FloatField(blank=True, default=0.0, help_text='Analytical A1')
    AEA2 = models.FloatField(blank=True, default=0.0)
    AEA3 = models.FloatField(blank=True, default=0.0)
    AEA4 = models.FloatField(blank=True, default=0.0)
    AEA5 = models.FloatField(blank=True, default=0.0)
    GammaA = models.FloatField(blank=True, default=0.0)
    GammaB = models.FloatField(blank=True, default=0.0)
    DW1 = models.FloatField(blank=True, default=0.0, help_text='dw')
    DW2 = models.FloatField(blank=True, default=0.0)
    DW3 = models.FloatField(blank=True, default=0.0)
    DW4 = models.FloatField(blank=True, default=0.0)
    VM1 = models.FloatField(blank=True, default=0.0, help_text='Vm')
    VM2 = models.FloatField(blank=True, default=0.0)
    VM3 = models.FloatField(blank=True, default=0.0)
    VM4 = models.FloatField(blank=True, default=0.0)
    VM5 = models.FloatField(blank=True, default=0.0)
    VM6 = models.FloatField(blank=True, default=0.0)
    VM7 = models.FloatField(blank=True, default=0.0)
    VM8 = models.FloatField(blank=True, default=0.0)
    VM9 = models.FloatField(blank=True, default=0.0)
    VM10 = models.FloatField(blank=True, default=0.0)
    NoCheck = models.BooleanField(blank=True, default=False)
    MoleBalance = models.CharField(max_length=50, blank=True, default='')

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Reaction)

@python_2_unicode_compatible  # only if you need to support Python 2
class Phases(models.Model):
    Units = (
        ('kJ/mol', 'kJ'),
        ('kcal/mol', 'kcal'),
        ('J/mol', 'J'),
        ('cal/mol', 'cal'),
    )
    PhaseName = models.CharField(max_length=100, blank=True, default='')
    Reaction = models.CharField(max_length=200, blank=True, default='')
    LogK = models.FloatField(blank=True, default=0.0)
    DeltaH = models.FloatField(blank=True, default=0.0)
    DeltaHUnits = models.CharField(choices=Units, max_length=10, default='kJ/mol')
    AEA1 = models.FloatField(blank=True, default=0.0, help_text='Analytical A1')
    AEA2 = models.FloatField(blank=True, default=0.0)
    AEA3 = models.FloatField(blank=True, default=0.0)
    AEA4 = models.FloatField(blank=True, default=0.0)
    AEA5 = models.FloatField(blank=True, default=0.0)
    TC = models.FloatField(blank=True, default=0.0)
    PC = models.FloatField(blank=True, default=0.0)
    OMEGA = models.FloatField(blank=True, default=0.0)
    VM1 = models.FloatField(blank=True, default=0.0, help_text='Vm')
    VM2 = models.FloatField(blank=True, default=0.0)
    VM3 = models.FloatField(blank=True, default=0.0)
    VM4 = models.FloatField(blank=True, default=0.0)
    VM5 = models.FloatField(blank=True, default=0.0)
    VM6 = models.FloatField(blank=True, default=0.0)
    VM7 = models.FloatField(blank=True, default=0.0)
    VM8 = models.FloatField(blank=True, default=0.0)
    VM9 = models.FloatField(blank=True, default=0.0)
    VM10 = models.FloatField(blank=True, default=0.0)

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Reaction)

@python_2_unicode_compatible  # only if you need to support Python 2
class SurfaceMasterSpecies(models.Model):
    BindingSite = models.CharField(max_length=20, blank=True, default='')
    SurfaceMaster = models.CharField(max_length=20, blank=True, default='')

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.BindingSite)

@python_2_unicode_compatible  # only if you need to support Python 2
class SurfaceSpecies(models.Model):
    Reaction = models.CharField(max_length=200, blank=True, default='')
    LogK = models.FloatField(blank=True, default=0.0)

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Reaction)

@python_2_unicode_compatible  # only if you need to support Python 2
class ExchangeMasterSpecies(models.Model):
    ExchangeName = models.CharField(max_length=20, blank=True, default='')
    ExchangeMaster = models.CharField(max_length=20, blank=True, default='')

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.ExchangeName)

@python_2_unicode_compatible  # only if you need to support Python 2
class ExchangeSpecies(models.Model):
    Units = (
        ('kJ/mol', 'kJ'),
        ('kcal/mol', 'kcal'),
        ('J/mol', 'J'),
        ('cal/mol', 'cal'),
    )
    Reaction = models.CharField(max_length=200, blank=True, default='')
    LogK = models.FloatField(blank=True, default=0.0)
    DeltaH = models.FloatField(blank=True, default=0.0)
    DeltaHUnits = models.CharField(choices=Units, max_length=10, default='kJ/mol')
    GammaA = models.FloatField(blank=True, default=0.0)
    GammaB = models.FloatField(blank=True, default=0.0)
    Davies = models.BooleanField(blank=True, default=False)

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Reaction)

@python_2_unicode_compatible  # only if you need to support Python 2
class Rates(models.Model):
    Name = models.CharField(max_length=20, blank=True, default='')
    BasicStatement = models.TextField(blank=True, default='')

    Note = models.TextField(blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    DBSource = models.ForeignKey('DBSources', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Name)

@python_2_unicode_compatible  # only if you need to support Python 2
class Refs(models.Model):
    RefID = models.CharField(max_length=20, blank=True, null=True, unique=True)
    Reference = models.CharField(max_length=500, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.RefID)


@python_2_unicode_compatible  # only if you need to support Python 2
class DBSources(models.Model):
    DBID = models.CharField(max_length=20, blank=True, null=True, unique=True)
    DBNote = models.CharField(max_length=500, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.DBID)

