from __future__ import unicode_literals

from django.db import models
from django import forms
from django.forms import ModelForm
from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

def user_directory_path(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'gsolv/jobs/{0}/{1}'.format(instance.JobID, filename)

def user_directory_pathP1(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'gsolv/jobs/{0}/gas_{1}'.format(instance.JobID, filename)

@python_2_unicode_compatible  # only if you need to support Python 2
class GSolvJob(models.Model):
    QMSoftwares = (
        ('Gaussian', 'Gaussian'),
        ('NWChem', 'NWChem'),
        #('Arrows', 'EMSL Arrows (online)'),
    )

    FileTypes = (
        ('xyz', 'xyz'),
        ('pdb', 'pdb'),
        ('sdf', 'sdf'),
        ('mol2', 'mol2'),
    )

    QMCalTypes = (
        ('Opt-Freq', 'Optimization and Frequencies'),
        ('Opt', 'Geometry Optimization'),
        ('Freq', 'Frequencies'),
        ('Energy', 'Single Point Energy'),
    )

    QMFunctionals = (
        ('M06-2X', 'M06-2X'),
        ('M06-L', 'M06-L'),
        ('B3LYP', 'B3LYP'),
        ('HF', 'HF'),
    )

    QMBasisSets = (
        ('6-31+G(d,p)', '6-31+G(d,p)'),
        ('6-31+G(d)', '6-31+G(d)'),
    )

    QMCoordinateFormats = (
        ('Cartesian', 'Cartesian'),
    )

    QMSolvationModels = (
        ('SMD', 'SMD'),
    )

    QMSolvents = (
        ('water', 'water'),
    )

    QMCavitySurfaces = (
        ('Default', 'Software Default'),
        ('SAS', 'Solvent Accessible Surface'),
        ('SES', 'Solvent Excluding Surface'),
        ('VDW', 'Van der Waals Surface'),
    )

    JobStatus = (
        ('0', 'to be start'),
        ('1', 'running'),
        ('2', 'finished'),
        ('3', 'something wrong'),
    )


    JobID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=50, blank=True, default='gsolv')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    SmilesStr = models.CharField(max_length=200, blank=True, default='')
    UploadedFile = models.FileField(upload_to=user_directory_path, blank=True)
    UploadedFileType = models.CharField(max_length=10, choices=FileTypes, default='')

    QMSoftware = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitle = models.CharField(max_length=100, blank=True, default='AQUA-MER GSOLV')
    QMCalType = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessors = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(32), MinValueValidator(1)])
    QMMemory = models.PositiveIntegerField(blank=True, default=1)
    QMFunctional = models.CharField(max_length=30, choices=QMFunctionals, default='M06-2X')
    QMBasisSet = models.CharField(max_length=30, choices=QMBasisSets, default='6-31+G(d,p)')
    QMCharge = models.IntegerField(blank=True, default=0)
    QMMultiplicity = models.IntegerField(blank=True, default=1)
    QMCoordinateFormat = models.CharField(max_length=30, choices=QMCoordinateFormats, default='Cartesian')
    QMSolvationModel = models.CharField(max_length=30, choices=QMSolvationModels, default='SMD')
    QMSolvent = models.CharField(max_length=30, choices=QMSolvents, default='water')
    QMCavitySurface = models.CharField(max_length=30, choices=QMCavitySurfaces, default='SAS')
    QMScalingFactor = models.DecimalField(max_digits=5, decimal_places=3, default=0.485)


    Note = models.CharField(max_length=100, blank=True, default='')

    # these columns are for output files
    UploadedOutputFile = models.FileField(upload_to=user_directory_path, blank=True)
    QMSoftwareOutput = models.CharField(max_length=30, default='')
    UploadedOutputFileP1 = models.FileField(upload_to=user_directory_pathP1, blank=True)
    QMSoftwareOutputP1 = models.CharField(max_length=30, default='')

    EnergyfromOutputFiles = models.CharField(max_length=30, default='')
    EnergyfromOutputFilesP1 = models.CharField(max_length=30, default='')
    GsolvCorrected = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)

    def __str__(self):
        return str(self.pk)


class SmilesForm(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStr']
        labels = {
            'SmilesStr': _('Provide the SMILES of your molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStr': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, 'required': True}),
        }

class UploadForm(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFile', 'UploadedFileType']
        labels = {
            'UploadedFile': _('Upload your structure file'),
            'UploadedFileType': _('Format'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedFile': forms.FileInput(attrs={'required': True}),
        }

class QueryForm(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

class GsolvInputForm(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'QMSoftware', 'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet',
                  'QMCharge', 'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent',
                  'QMCavitySurface', 'QMScalingFactor']
        labels = {
            'QMSoftware': _('Software'),
            'QMTitle': _('Title of calculations'),
            'QMCalType': _('Type of calculations'),
            'QMProcessors': _('Number of processors (max: 32)'),
            'QMMemory': _('Meory to use (unit: GB)'),
            'QMFunctional': _('Functional'),
            'QMBasisSet': _('BasisSet'),
            'QMCharge': _('Charge'),
            'QMMultiplicity': _('Multiplicity'),
            'QMCoordinateFormat': _('Format of the coordinates'),
            'QMSolvationModel': _('Solvation model'),
            'QMSolvent': _('Solvent'),
            'QMCavitySurface': _('Surface type for the cavity'),
            'QMScalingFactor': _('Scaling factor for the cavity'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }

class UploadOutputForm(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedOutputFile']
        labels = {
            'UploadedOutputFile': _('Upload output file for AQUEOUS phase calculation'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedOutputFile': forms.FileInput(attrs={'required': True}),
        }

class UploadOutputFormP1(ModelForm):
    class Meta:
        model = GSolvJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedOutputFileP1']
        labels = {
            'UploadedOutputFileP1': _('Upload output file for GAS phase calculation'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedOutputFileP1': forms.FileInput(attrs={'required': True}),
        }
