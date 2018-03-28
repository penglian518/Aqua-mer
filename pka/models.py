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
    return 'pka/jobs/{0}/A_{1}'.format(instance.JobID, filename)

def user_directory_pathP1(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'pka/jobs/{0}/HA_{1}'.format(instance.JobID, filename)

@python_2_unicode_compatible  # only if you need to support Python 2
class pKaJob(models.Model):
    QMSoftwares = (
        ('Gaussian', 'Gaussian'),
        ('NWChem', 'NWChem'),
        ('Arrows', 'EMSL Arrows (online)'),
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
    Name = models.CharField(max_length=50, blank=True, default='pka')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField('date created', default=datetime.now())

    SmilesStr = models.CharField(max_length=200, blank=True, default='')
    UploadedFile = models.FileField(upload_to=user_directory_path, blank=True)
    UploadedFileType = models.CharField(max_length=10, choices=FileTypes, default='')

    QMSoftware = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitle = models.CharField(max_length=100, blank=True, default='AQUA-MER pKa Calculation')
    QMCalType = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessors = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
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

    SmilesStrP1 = models.CharField(max_length=200, blank=True, default='')
    UploadedFileP1 = models.FileField(upload_to=user_directory_pathP1, blank=True)
    UploadedFileTypeP1 = models.CharField(max_length=10, choices=FileTypes, default='')

    QMSoftwareP1 = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitleP1 = models.CharField(max_length=100, blank=True, default='AQUA-MER pKa Calculation')
    QMCalTypeP1 = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessorsP1 = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
    QMMemoryP1 = models.PositiveIntegerField(blank=True, default=1)
    QMFunctionalP1 = models.CharField(max_length=30, choices=QMFunctionals, default='M06-2X')
    QMBasisSetP1 = models.CharField(max_length=30, choices=QMBasisSets, default='6-31+G(d,p)')
    QMChargeP1 = models.IntegerField(blank=True, default=0)
    QMMultiplicityP1 = models.IntegerField(blank=True, default=1)
    QMCoordinateFormatP1 = models.CharField(max_length=30, choices=QMCoordinateFormats, default='Cartesian')
    QMSolvationModelP1 = models.CharField(max_length=30, choices=QMSolvationModels, default='SMD')
    QMSolventP1 = models.CharField(max_length=30, choices=QMSolvents, default='water')
    QMCavitySurfaceP1 = models.CharField(max_length=30, choices=QMCavitySurfaces, default='SAS')
    QMScalingFactorP1 = models.DecimalField(max_digits=5, decimal_places=3, default=0.485)

    NoteP1 = models.CharField(max_length=100, blank=True, default='')


    def __str__(self):
        return str(self.pk)


class SmilesForm(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStr']
        labels = {
            'SmilesStr': _('Provide the SMILES of your "deprotonated (A-)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStr': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, }),
        }


class UploadForm(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFile', 'UploadedFileType']
        labels = {
            'UploadedFile': _('Upload your structure file for "deprotonated (A-)" molecule'),
            'UploadedFileType': _('Format'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedFile': forms.FileInput(attrs={'required': True}),
        }


class SmilesFormP1(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStrP1']
        labels = {
            'SmilesStrP1': _('Provide the SMILES of your "protonated (HA)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStrP1': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, }),
        }

class UploadFormP1(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFileP1', 'UploadedFileTypeP1']
        labels = {
            'UploadedFileP1': _('Upload your structure file for "protonated (HA)" molecule'),
            'UploadedFileTypeP1': _('Format'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedFileP1': forms.FileInput(attrs={'required': True}),
        }



class QueryForm(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

class pKaInputForm(ModelForm):
    class Meta:
        model = pKaJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'QMSoftware', 'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet',
                  'QMCharge', 'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent',
                  'QMCavitySurface', 'QMScalingFactor',
                  'QMSoftwareP1', 'QMTitleP1', 'QMCalTypeP1', 'QMProcessorsP1', 'QMMemoryP1', 'QMFunctionalP1', 'QMBasisSetP1',
                  'QMChargeP1', 'QMMultiplicityP1', 'QMCoordinateFormatP1', 'QMSolvationModelP1', 'QMSolventP1',
                  'QMCavitySurfaceP1', 'QMScalingFactorP1',
                  ]
        labels = {
            'QMSoftware': _('Software'),
            'QMTitle': _('Title of calculations'),
            'QMCalType': _('Type of calculations'),
            'QMProcessors': _('Number of processors (max: 4)'),
            'QMMemory': _('Meory to use (unit: GB, max: 2)'),
            'QMFunctional': _('Functional'),
            'QMBasisSet': _('BasisSet'),
            'QMCharge': _('Charge'),
            'QMMultiplicity': _('Multiplicity'),
            'QMCoordinateFormat': _('Format of the coordinates'),
            'QMSolvationModel': _('Solvation model'),
            'QMSolvent': _('Solvent'),
            'QMCavitySurface': _('Surface type for the cavity'),
            'QMScalingFactor': _('Scaling factor for the cavity'),

            'QMSoftwareP1': _('Software'),
            'QMTitleP1': _('Title of calculations'),
            'QMCalTypeP1': _('Type of calculations'),
            'QMProcessorsP1': _('Number of processors (max: 4)'),
            'QMMemoryP1': _('Meory to use (unit: GB, max: 2)'),
            'QMFunctionalP1': _('Functional'),
            'QMBasisSetP1': _('BasisSet'),
            'QMChargeP1': _('Charge'),
            'QMMultiplicityP1': _('Multiplicity'),
            'QMCoordinateFormatP1': _('Format of the coordinates'),
            'QMSolvationModelP1': _('Solvation model'),
            'QMSolventP1': _('Solvent'),
            'QMCavitySurfaceP1': _('Surface type for the cavity'),
            'QMScalingFactorP1': _('Scaling factor for the cavity'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }
