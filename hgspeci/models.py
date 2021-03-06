from __future__ import unicode_literals

from django.db import models
from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from dal import autocomplete
from phreeqcdb.models import SolutionMasterSpecies

# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class HgSpeciJob(models.Model):
    # job info

    JobStatus = (
        ('0', 'to be start'),
        ('1', 'running'),
        ('2', 'finished'),
        ('3', 'something wrong'),
    )

    Units = (
        ('ppt', 'ppt (parts per thousand)'),
        ('ppm', 'ppm (parts per million)'),
        ('ppb', 'ppb (parts per billion)'),

        ('mol/L', 'mol/L (mole per liter)'),
        ('umol/L', 'umol/L (micromoles per liter)'),
        ('mmol/L', 'mmol/L (millimoles per liter)'),
        ('g/L', 'g/L (gram per liter)'),
        ('ug/L', 'ug/L (micrograms per liter)'),
        ('mg/L', 'mg/L (milligrams per liter)'),

        ('mol/kgw', 'mol/kgw (mole per kilogram water)'),
        ('umol/kgw', 'umol/kgw (micromoles per kilogram water)'),
        ('mmol/kgw', 'mmol/kgw (millimoles per kilogram water)'),
        ('g/kgw', 'g/kgw (gram per kilogram water)'),
        ('ug/kgw', 'ug/kgw (micrograms per kilogram water)'),
        ('mg/kgw', 'mg/kgw (milligrams per kilogram water)'),

        ('mol/kgs', 'mol/kgs (mole per kilogram solution)'),
        ('umol/kgs', 'umol/kgs (micromoles per kilogram solution)'),
        ('mmol/kgs', 'mmol/kgs (millimoles per kilogram solution)'),
        ('g/kgs', 'g/kgs (gram per kilogram solution)'),
        ('ug/kgs', 'ug/kgs (micrograms per kilogram solution)'),
        ('mg/kgs', 'mg/kgs (milligrams per kilogram solution)'),

    )

    RedoxMethods = (
        ('pe', 'pe'),
        ('couple', 'Redox Couple'),
    )

    Titrants = (
        ('NaOH', 'NaOH'),
        ('HCl', 'HCl'),
        ('HNO3', 'HNO3'),
        ('H2SO4', 'H2SO4'),
    )

    Databases = (
        ('phreeqc', 'phreeqc'),
        ('phreeqc+aquamer', 'phreeqc+aquamer'),
        ('phreeqc+calc', 'phreeqc+calc'),
        ('phreeqc+aquamer+calc', 'phreeqc+aquamer+calc'),
    )

    # use self.id or self.pk as JobID
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=50, blank=True, default='HgSpeci')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    # input file
    SPTitle = models.CharField(max_length=100, default='AQUA-MER SOLUTION')
    SPUnit = models.CharField(max_length=10, choices=Units, default='mol/L')
    SPTemperature = models.FloatField(blank=False, default=25.0)
    SPpHMin = models.FloatField(blank=False, default=0.0)
    SPpHMax = models.FloatField(blank=False, default=14.0)
    SPpHIncrease = models.FloatField(blank=False, default=1.0)
    SPRedoxMethod = models.CharField(max_length=10, choices=RedoxMethods, default='pe')
    SPRedoxValue = models.CharField(max_length=20, default='4.0')
    SPDensity = models.FloatField(blank=False, default=1.0)
    SPTitrant = models.CharField(max_length=10, choices=Titrants, default='pe')
    SPTitrantConcentration = models.FloatField(max_length=20, default=10.0)
    SPDBtoUse = models.CharField(max_length=20, choices=Databases, default='phreeqc+aquamer')
    SPUserDefinedInput = models.TextField(blank=True, default='')

    # do not use anymore
    SPpe = models.FloatField(blank=False, default=4.0)                   # not use anymore
    SPRedox = models.CharField(max_length=20, default='O(-2)/O(0)')      # not use anymore

    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible  # only if you need to support Python 2
class SPElements(models.Model):
    SPJobID = models.ForeignKey('HgSpeciJob', on_delete=models.CASCADE, default=0, related_name='spelements')
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Element = models.CharField(max_length=50, blank=True, default='')
    Concentration = models.FloatField(blank=True)
    Unit = models.CharField(max_length=50, blank=True, default='')
    AS = models.BooleanField(blank=True, default=False)
    ASFormula = models.CharField(max_length=50, blank=True, default='')
    GFW = models.BooleanField(blank=True, default=False)
    GFWFormula = models.CharField(max_length=50, blank=True, default='')
    Redox = models.CharField(max_length=50, blank=True, default='')
    Others = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return str(self.pk)

class SPDBtoUseForm(ModelForm):
    class Meta:
        model = HgSpeciJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SPDBtoUse']
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }
        labels = {
            'SPDBtoUse': _('Database to use'),
        }




class ParameterForm(ModelForm):
    """
    for build up input file, excluding elements & concentrations which are handled by a separate formset
    """
    class Meta:
        model = HgSpeciJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SPTitle', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease',
                  'SPRedoxMethod', 'SPRedoxValue', 'SPDensity', 'SPUnit', 'SPTitrant', 'SPTitrantConcentration']
        labels = {
            'SPTitle': _('Title'),
            'SPUnit': _('Concentration Units'),
            'SPTemperature': _('Temperature (C)'),
            'SPpHMin': _('pH (min)'),
            'SPpHMax': _('pH (max)'),
            'SPpHIncrease': _('pH (increment)'),
            'SPRedoxMethod': _('Redox state calculation options'),
            'SPRedoxValue': _('pe value/redox couple'),
            'SPDensity': _('Density'),
            'SPTitrant': _('Titrant'),
            'SPTitrantConcentration': _('Titrant concentration'),
        }
        help_texts = {
            'SPTitle': _('(Title for this solution)'),
            'SPpHIncrease': _('(For single pH solution, set pH (max) equal to pH (min))'),
            'SPRedoxMethod': _('(Select one of the methods to calculate redox state)'),
            'SPRedoxValue': _('(If using redox couple (e.g. O(-2)/O(0) ), make sure include one/both species in the Elements/Species section.)'),
            'SPDensity': _('(Density of the solution, kg/L)'),
            'SPUnit': _('(Default concentration unit for elements in this solution)'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SPTitle': forms.TextInput(attrs={'size': 40}),
        }

class UserDefineForm(ModelForm):
    """
    for build up input file, excluding elements & concentrations which are handled by a separate formset
    """
    class Meta:
        model = HgSpeciJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SPUserDefinedInput']
        labels = {
            'SPUserDefinedInput': _('User-defined input file'),
        }
        help_texts = {
            'SPUserDefinedInput': _('Please provide a complete input file.'),

        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SPUserDefinedInput': forms.Textarea(attrs={'style': 'width: 80%;'}),
        }


class SPElementsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # call parent's constructor
        super(SPElementsForm, self).__init__(*args, **kwargs)


    class Meta:
        model = SPElements
        fields = ['JobID', 'Element', 'Concentration', 'Unit', 'AS', 'ASFormula', 'GFW', 'GFWFormula', 'Redox', 'Others']
        widgets = {
            'JobID': forms.HiddenInput(),
            'Element': forms.TextInput(attrs={'class': 'dyn-input', 'size': 20, 'required': True}),
            'Concentration': forms.TextInput(attrs={'size': 15, 'required': True}),
            'Unit': forms.TextInput(attrs={'placeholder': 'Unit for this element, if different.', 'size': 25}),
            'ASFormula': forms.TextInput(attrs={'placeholder': 'formula if use "AS".', 'size': 20}),
            'GFWFormula': forms.TextInput(attrs={'placeholder': 'formula if use "GFW".', 'size': 20}),
            'Redox': forms.TextInput(attrs={'placeholder': 'Redox couple for this element, if different.', 'size': 25}),
            'Others': forms.TextInput(attrs={'placeholder': 'optional keywords.', 'size': 25, 'title': 'additional'}),
        }
        labels = {
            'Element': _('Elements/Species'),
            'Unit': _('Concentration units'),
            'ASFormula': _('AS Formula'),
            'GFWFormula': _('GFW Formula'),
            'Redox': _('Redox couple'),
            'Others': _('Additional keywords'),
        }


@python_2_unicode_compatible  # only if you need to support Python 2
class SPMasterSpecies(models.Model):
    SPJobID = models.ForeignKey('HgSpeciJob', on_delete=models.CASCADE, default=0, related_name='spmaster')
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Element = models.CharField(max_length=50, blank=False, default='')
    Species = models.CharField(max_length=50, blank=False, default='')
    Alkalinity = models.FloatField(blank=False, default=0.0)
    GFWorFormula = models.CharField(max_length=50, blank=False, default='0.0')
    GFWforElement = models.FloatField(blank=True, default=0.0)

    Note = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return str(self.pk)


class SPMasterSpeciesForm(ModelForm):
    class Meta:
        model = SPMasterSpecies
        fields = ['JobID', 'Element', 'Species', 'Alkalinity', 'GFWorFormula', 'GFWforElement', 'Note']
        widgets = {
            'JobID': forms.HiddenInput(),
        }
        labels = {
            'GFWorFormula': _('GFW or Formula'),
        }

        # TODO, if the user leave with blank, fill with default value!
        def clean_field(self):
            data = self.cleaned_data['field']
            if not data:
                data = 'default value'
            return data


@python_2_unicode_compatible  # only if you need to support Python 2
class SPSolutionSpecies(models.Model):
    Units = (
        ('kJ/mol', 'kJ'),
        ('kcal/mol', 'kcal'),
        ('J/mol', 'J'),
        ('cal/mol', 'cal'),
    )
    SPJobID = models.ForeignKey('HgSpeciJob', on_delete=models.CASCADE, default=0, related_name='spspecies')
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Reaction = models.CharField(max_length=200, blank=False, default='')
    LogK = models.FloatField(blank=False, default=0.0)
    DeltaH = models.FloatField(blank=True, null=True, default=0.0)
    DeltaHUnits = models.CharField(choices=Units, max_length=10, default='kJ/mol')
    AEA1 = models.FloatField(blank=True, null=True, default=0.0, help_text='Analytical A1')
    AEA2 = models.FloatField(blank=True, null=True, default=0.0)
    AEA3 = models.FloatField(blank=True, null=True, default=0.0)
    AEA4 = models.FloatField(blank=True, null=True, default=0.0)
    AEA5 = models.FloatField(blank=True, null=True, default=0.0)
    AEA6 = models.FloatField(blank=True, null=True, default=0.0)
    DW1 = models.FloatField(blank=True, null=True, default=0.0)
    DW2 = models.FloatField(blank=True, null=True, default=0.0)
    DW3 = models.FloatField(blank=True, null=True, default=0.0)
    DW4 = models.FloatField(blank=True, null=True, default=0.0)
    VM1 = models.FloatField(blank=True, null=True, default=0.0)
    VM2 = models.FloatField(blank=True, null=True, default=0.0)
    VM3 = models.FloatField(blank=True, null=True, default=0.0)
    VM4 = models.FloatField(blank=True, null=True, default=0.0)
    VM5 = models.FloatField(blank=True, null=True, default=0.0)
    VM6 = models.FloatField(blank=True, null=True, default=0.0)
    VM7 = models.FloatField(blank=True, null=True, default=0.0)
    VM8 = models.FloatField(blank=True, null=True, default=0.0)
    VM9 = models.FloatField(blank=True, null=True, default=0.0)
    VM10 = models.FloatField(blank=True, null=True, default=0.0)
    GammaA = models.FloatField(blank=True, null=True, default=0.0)
    GammaB = models.FloatField(blank=True, null=True, default=0.0)
    NoCheck = models.BooleanField(blank=True, default=False)
    MoleBalance = models.CharField(max_length=50, blank=True, null=True, default='')

    Note = models.CharField(max_length=200, blank=True, null=True, default='')

    def __str__(self):
        return str(self.pk)

class SPSolutionSpeciesForm(ModelForm):
    class Meta:
        model = SPSolutionSpecies
        fields = ['JobID', 'Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'GammaA', 'GammaB',
                  'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5', 'AEA6',
                  'DW1', 'DW2', 'DW3', 'DW4', 'VM1', 'VM2', 'VM3', 'VM4', 'VM5', 'VM6', 'VM7', 'VM8', 'VM9', 'VM10',
                  'NoCheck', 'MoleBalance', 'Note']
        widgets = {
            'JobID': forms.HiddenInput(),
            'LogK': forms.TextInput(attrs={'size': 7}),
            'DeltaH': forms.TextInput(attrs={'size': 7}),
            'AEA1': forms.TextInput(attrs={'size': 5}),
            'AEA2': forms.TextInput(attrs={'size': 5}),
            'AEA3': forms.TextInput(attrs={'size': 5}),
            'AEA4': forms.TextInput(attrs={'size': 5}),
            'AEA5': forms.TextInput(attrs={'size': 5}),
            'AEA6': forms.TextInput(attrs={'size': 5}),
            'DW1': forms.TextInput(attrs={'size': 5}),
            'DW2': forms.TextInput(attrs={'size': 5}),
            'DW3': forms.TextInput(attrs={'size': 5}),
            'DW4': forms.TextInput(attrs={'size': 5}),
            'VM1': forms.TextInput(attrs={'size': 5}),
            'VM2': forms.TextInput(attrs={'size': 5}),
            'VM3': forms.TextInput(attrs={'size': 5}),
            'VM4': forms.TextInput(attrs={'size': 5}),
            'VM5': forms.TextInput(attrs={'size': 5}),
            'VM6': forms.TextInput(attrs={'size': 5}),
            'VM7': forms.TextInput(attrs={'size': 5}),
            'VM8': forms.TextInput(attrs={'size': 5}),
            'VM9': forms.TextInput(attrs={'size': 5}),
            'VM10': forms.TextInput(attrs={'size': 5}),
            'GammaA': forms.TextInput(attrs={'size': 7}),
            'GammaB': forms.TextInput(attrs={'size': 7}),
            'MoleBalance': forms.TextInput(attrs={'size': 10}),
            'Note': forms.TextInput(attrs={'size': 10}),
        }
        labels = {
            'DeltaHUnits': _('Unit'),
            'AEA1': _('A1'),
            'AEA2': _('A2'),
            'AEA3': _('A3'),
            'AEA4': _('A4'),
            'AEA5': _('A5'),
            'AEA6': _('A6'),
            'DW1': _('dw1'),
            'DW2': _('dw2'),
            'DW3': _('dw3'),
            'DW4': _('dw4'),
            'VM1': _('Vm1'),
            'VM2': _('Vm2'),
            'VM3': _('Vm3'),
            'VM4': _('Vm4'),
            'VM5': _('Vm5'),
            'VM6': _('Vm6'),
            'VM7': _('Vm7'),
            'VM8': _('Vm8'),
            'VM9': _('Vm9'),
            'VM10': _('Vm10'),
        }


class QueryForm(ModelForm):
    class Meta:
        model = HgSpeciJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

