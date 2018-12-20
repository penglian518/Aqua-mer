from __future__ import unicode_literals

from django.db import models

from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _

# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class CalcSolutionMasterSpecies(models.Model):
    Element = models.CharField(max_length=100, blank=True, default='')
    Species = models.CharField(max_length=100, blank=True, default='')
    Alkalinity = models.FloatField(blank=True, default=0.0)
    GFWorFormula = models.CharField(max_length=100, blank=True, default='0.0')
    GFWforElement = models.FloatField(blank=True, null=True)

    Charge = models.IntegerField(blank=True, default=0)
    PubChemID = models.PositiveIntegerField(blank=True, null=True)
    IUPACName = models.CharField(max_length=200, blank=True, default='')
    SMILES = models.CharField(max_length=200, blank=True, default='')
    XYZ = models.CharField(max_length=200, blank=True, default='')

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)
    Source = models.CharField(max_length=200, blank=True, default='')


    def __str__(self):
        return str(self.Element)

@python_2_unicode_compatible  # only if you need to support Python 2
class CalcSolutionSpecies(models.Model):
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
    NoCheck = models.BooleanField(blank=True, default=False)
    MoleBalance = models.CharField(max_length=50, blank=True, default='')

    Software = models.CharField(max_length=50, blank=True, default='Gaussian 09')
    SoftwareVersion = models.CharField(max_length=50, blank=True, default='E. 01')
    Functional = models.CharField(max_length=50, blank=True, default='M06-2X')
    BasisSet = models.CharField(max_length=50, blank=True, default='6-31+G(d,p)')
    SolvationModel = models.CharField(max_length=50, blank=True, default='sSAS')

    Note = models.CharField(max_length=200, blank=True, default='')
    Ref = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.Reaction)

@python_2_unicode_compatible  # only if you need to support Python 2
class Refs(models.Model):
    RefID = models.CharField(max_length=20, blank=True, null=True, unique=True)
    Reference = models.CharField(max_length=500, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.RefID)
