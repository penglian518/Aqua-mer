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
        ('ppt', 'parts per thousand (ppt)'),
        ('ppm', 'parts per million (ppm)'),
        ('ppb', 'parts per billion (ppb)'),

        ('mol/L', 'mole per liter (mol/L)'),
        ('umol/L', 'micromoles per liter (umol/L)'),
        ('mmol/L', 'millimoles per liter (mmol/L)'),
        ('g/L', 'gram per liter (g/L)'),
        ('ug/L', 'micrograms per liter (ug/L)'),
        ('mg/L', 'milligrams per liter (mg/L)'),

        ('mol/kgw', 'mole per kilogram water (mol/kgw)'),
        ('umol/kgw', 'micromoles per kilogram water (umol/kgw)'),
        ('mmol/kgw', 'millimoles per kilogram water (mmol/kgw)'),
        ('g/kgw', 'gram per kilogram water (g/kgw)'),
        ('ug/kgw', 'micrograms per kilogram water (ug/kgw)'),
        ('mg/kgw', 'milligrams per kilogram water (mg/kgw)'),

        ('mol/kgs', 'mole per kilogram solution (mol/kgs)'),
        ('umol/kgs', 'micromoles per kilogram solution (umol/kgs)'),
        ('mmol/kgs', 'millimoles per kilogram solution (mmol/kgs)'),
        ('g/kgs', 'gram per kilogram solution (g/kgs)'),
        ('ug/kgs', 'micrograms per kilogram solution (ug/kgs)'),
        ('mg/kgs', 'milligrams per kilogram solution (mg/kgs)'),

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
    SPpe = models.FloatField(blank=False, default=4.0)
    SPRedox = models.CharField(max_length=20, default='O(-2)/O(0)')
    SPDensity = models.FloatField(blank=False, default=1.0)



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


class ParameterForm(ModelForm):
    """
    for build up input file, excluding elements & concentrations which are handled by a separate formset
    """
    class Meta:
        model = HgSpeciJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SPTitle', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease',
                  'SPpe', 'SPRedox', 'SPDensity', 'SPUnit']
        labels = {
            'SPTitle': _('Title'),
            'SPUnit': _('Concentration Units'),
            'SPTemperature': _('Temperature (C)'),
            'SPpHMin': _('pH (min)'),
            'SPpHMax': _('pH (max)'),
            'SPpHIncrease': _('pH (increment)'),
            'SPpe': _('pe'),
            'SPRedox': _('Redox'),
            'SPDensity': _('Density'),
        }
        help_texts = {
            'SPTitle': _('(Title for this solution)'),
            'SPpe': _('(Conventional negative log of the activity of the electron. For distributing redox elements and calculating saturation indices)'),
            'SPRedox': _('(A redox couple used to calculate pe)'),
            'SPDensity': _('(Density of the solution, kg/L)'),
            'SPUnit': _('(Default concentration unit for elements in this solution)'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SPTitle': forms.TextInput(attrs={'size': 40}),

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
        fields = ['JobID', 'Reaction', 'LogK', 'DeltaH', 'DeltaHUnits', 'AEA1', 'AEA2', 'AEA3', 'AEA4', 'AEA5',
                  'GammaA', 'GammaB', 'NoCheck', 'MoleBalance', 'Note']
        widgets = {
            'JobID': forms.HiddenInput(),
            'LogK': forms.TextInput(attrs={'size': 7}),
            'DeltaH': forms.TextInput(attrs={'size': 7}),
            'AEA1': forms.TextInput(attrs={'size': 5}),
            'AEA2': forms.TextInput(attrs={'size': 5}),
            'AEA3': forms.TextInput(attrs={'size': 5}),
            'AEA4': forms.TextInput(attrs={'size': 5}),
            'AEA5': forms.TextInput(attrs={'size': 5}),
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
        }


class QueryForm(ModelForm):
    class Meta:
        model = HgSpeciJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

