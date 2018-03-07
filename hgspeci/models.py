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
        ('ppm', 'ppm'),
        ('ppd', 'ppd'),
    )

    # use self.id or self.pk as JobID
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=50, blank=True, default='HgSpeci')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField('date created', default=datetime.now())

    # input file
    SPTitle = models.CharField(max_length=100, default='AQUA-MER SOLUTION')
    SPUnit = models.CharField(max_length=10, choices=Units, default='ppm')
    SPTemperature = models.FloatField(blank=False, default=25.0)
    SPpHMin = models.FloatField(blank=False, default=0.0)
    SPpHMax = models.FloatField(blank=False, default=14.0)
    SPpHIncrease = models.FloatField(blank=False, default=1.0)


    def __str__(self):
        return str(self.pk)


@python_2_unicode_compatible  # only if you need to support Python 2
class SPElements(models.Model):
    SPJobID = models.ForeignKey('HgSpeciJob', on_delete=models.CASCADE, default=0, related_name='spelements')
    JobID = models.PositiveIntegerField(blank=True, default=0)
    Element = models.CharField(max_length=50, blank=True, default='')
    Concentration = models.FloatField(blank=True)
    PE = models.BooleanField(blank=True, default=False)
    PPB = models.BooleanField(blank=True, default=False)
    PPBFormula = models.CharField(max_length=50, blank=True, default='')
    Others = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return str(self.pk)

class SPElementsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # call parent's constructor
        super(SPElementsForm, self).__init__(*args, **kwargs)
        # turn on required for concentration field
        self.fields['Concentration'].required = True


    class Meta:
        model = SPElements
        fields = ['JobID', 'Element', 'Concentration', 'PE', 'PPB', 'PPBFormula', 'Others']
        widgets = {
            'JobID': forms.HiddenInput(),
            'Element': forms.TextInput(attrs={'class': 'dyn-input'}),
        }
        labels = {
            'PPBFormula': _('Formula for PPB'),
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






class ParameterForm(ModelForm):
    """
    for build up input file, excluding elements & concentrations which are handled by a separate formset
    """
    class Meta:
        model = HgSpeciJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SPTitle', 'SPUnit', 'SPTemperature', 'SPpHMin', 'SPpHMax', 'SPpHIncrease']
        labels = {
            'SPTitle': _('Title'),
            'SPUnit': _('Unit'),
            'SPTemperature': _('Temperature (C)'),
            'SPpHMin': _('pH (min)'),
            'SPpHMax': _('pH (max)'),
            'SPpHIncrease': _('pH (increment)'),
        }
        help_texts = {
            'SPTitle': _('(Title for this solution)'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SPTitle': forms.TextInput(attrs={'size': 40}),

        }


class QueryForm(ModelForm):
    class Meta:
        model = HgSpeciJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

