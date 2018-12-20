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
    return 'logk/jobs/{0}/L_{1}'.format(instance.JobID, filename)

def user_directory_pathP1(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'logk/jobs/{0}/ML_{1}'.format(instance.JobID, filename)

def user_directory_pathM(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'logk/jobs/{0}/M_{1}'.format(instance.JobID, filename)

@python_2_unicode_compatible  # only if you need to support Python 2
class LogKJob(models.Model):
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
        ('M06', 'M06'),
        ('M06-2X', 'M06-2X'),
        ('M06-L', 'M06-L'),
        ('B3LYP', 'B3LYP'),
        ('HF', 'HF'),
    )

    QMBasisSets = (
        ('6-31+G(d,p)', '6-31+G(d,p)'),
        ('6-31+G(d)', '6-31+G(d)'),
        ('SDD', 'SDD'),
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

    TransToMolecules = (
        ('A', 'Ligand (L-)'),
        ('HA', 'Complex (ML)'),
        ('None', "None of the above, I'll start over."),
    )

    QMMetals = (
        ('Hg2+', 'Hg2+'),
        ('Hg+', 'Hg+'),
    )



    JobID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=50, blank=True, default='logk')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField(auto_now_add=True)

    TransToA = models.CharField(max_length=10, choices=TransToMolecules, default='')

    # for the ligand molecule (L-)
    SmilesStr = models.CharField(max_length=200, blank=True, default='')
    UploadedFile = models.FileField(upload_to=user_directory_path, blank=True)
    UploadedFileType = models.CharField(max_length=10, choices=FileTypes, default='')

    QMSoftware = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitle = models.CharField(max_length=100, blank=True, default='Log K Calc (L-)')
    QMCalType = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessors = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
    QMMemory = models.PositiveIntegerField(blank=True, default=1)
    QMFunctional = models.CharField(max_length=30, choices=QMFunctionals, default='M06')
    QMBasisSet = models.CharField(max_length=30, choices=QMBasisSets, default='6-31+G(d,p)')
    QMCharge = models.IntegerField(blank=True, default=0)
    QMMultiplicity = models.IntegerField(blank=True, default=1)
    QMCoordinateFormat = models.CharField(max_length=30, choices=QMCoordinateFormats, default='Cartesian')
    QMSolvationModel = models.CharField(max_length=30, choices=QMSolvationModels, default='SMD')
    QMSolvent = models.CharField(max_length=30, choices=QMSolvents, default='water')
    QMCavitySurface = models.CharField(max_length=30, choices=QMCavitySurfaces, default='SAS')
    QMScalingFactor = models.DecimalField(max_digits=5, decimal_places=3, null=True)

    Note = models.CharField(max_length=100, blank=True, default='')

    # for the complex molecule (ML)
    SmilesStrP1 = models.CharField(max_length=200, blank=True, default='')
    UploadedFileP1 = models.FileField(upload_to=user_directory_pathP1, blank=True)
    UploadedFileTypeP1 = models.CharField(max_length=10, choices=FileTypes, default='')

    QMSoftwareP1 = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitleP1 = models.CharField(max_length=100, blank=True, default='Log K Calc (ML)')
    QMCalTypeP1 = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessorsP1 = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
    QMMemoryP1 = models.PositiveIntegerField(blank=True, default=1)
    QMFunctionalP1 = models.CharField(max_length=30, choices=QMFunctionals, default='M06')
    QMBasisSetP1 = models.CharField(max_length=30, choices=QMBasisSets, default='6-31+G(d,p)')
    QMChargeP1 = models.IntegerField(blank=True, default=0)
    QMMultiplicityP1 = models.IntegerField(blank=True, default=1)
    QMCoordinateFormatP1 = models.CharField(max_length=30, choices=QMCoordinateFormats, default='Cartesian')
    QMSolvationModelP1 = models.CharField(max_length=30, choices=QMSolvationModels, default='SMD')
    QMSolventP1 = models.CharField(max_length=30, choices=QMSolvents, default='water')
    QMCavitySurfaceP1 = models.CharField(max_length=30, choices=QMCavitySurfaces, default='SAS')
    QMScalingFactorP1 = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    #QMScalingFactorP1 = models.DecimalField(max_digits=5, decimal_places=3, choices=QMScalingFactors, default='1.08')

    NoteP1 = models.CharField(max_length=100, blank=True, default='')

    # for metal ions
    QMMetal = models.CharField(max_length=10, choices=QMMetals, default='Hg2+')

    QMSoftwareM = models.CharField(max_length=30, choices=QMSoftwares, default='Gaussian')

    QMTitleM = models.CharField(max_length=100, blank=True, default='Log K Calc (M+)')
    QMCalTypeM = models.CharField(max_length=30, choices=QMCalTypes, default='Opt-Freq')
    QMProcessorsM = models.PositiveIntegerField(blank=True, default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
    QMMemoryM = models.PositiveIntegerField(blank=True, default=1)
    QMFunctionalM = models.CharField(max_length=30, choices=QMFunctionals, default='M06')
    QMBasisSetM = models.CharField(max_length=30, choices=QMBasisSets, default='SDD')
    QMChargeM = models.IntegerField(blank=True, default=2)
    QMMultiplicityM = models.IntegerField(blank=True, default=1)
    QMCoordinateFormatM = models.CharField(max_length=30, choices=QMCoordinateFormats, default='Cartesian')
    QMSolvationModelM = models.CharField(max_length=30, choices=QMSolvationModels, default='SMD')
    QMSolventM = models.CharField(max_length=30, choices=QMSolvents, default='water')
    QMCavitySurfaceM = models.CharField(max_length=30, choices=QMCavitySurfaces, default='SAS')
    QMScalingFactorM = models.DecimalField(max_digits=5, decimal_places=3, null=True)

    NoteM = models.CharField(max_length=100, blank=True, default='')

    # these columns are for output files
    UploadedOutputFile = models.FileField(upload_to=user_directory_path, blank=True)
    QMSoftwareOutput = models.CharField(max_length=30, default='')
    UploadedOutputFileP1 = models.FileField(upload_to=user_directory_pathP1, blank=True)
    QMSoftwareOutputP1 = models.CharField(max_length=30, default='')
    UploadedOutputFileM = models.FileField(upload_to=user_directory_pathM, blank=True)
    QMSoftwareOutputM = models.CharField(max_length=30, default='')

    EnergyfromOutputFiles = models.CharField(max_length=30, default='')
    EnergyfromOutputFilesP1 = models.CharField(max_length=30, default='')
    EnergyfromOutputFilesM = models.CharField(max_length=30, default='')
    LogKfromOutputFiles = models.DecimalField(max_digits=15, decimal_places=3, default=0.0)




    def __str__(self):
        return str(self.JobID)


class MetalForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'QMMetal']
        labels = {
            'QMMetal': _('Select your "Metal ion (M+)"'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }


class SmilesForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStr']
        labels = {
            'SmilesStr': _('Provide the SMILES of your "Ligand (L-)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStr': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, }),
        }


class UploadForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFile', 'UploadedFileType']
        labels = {
            'UploadedFile': _('Upload your structure file for "Ligand (L-)" molecule'),
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
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStrP1']
        labels = {
            'SmilesStrP1': _('Provide the SMILES of your "Complex (ML)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStrP1': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, }),
        }

class UploadFormP1(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFileP1', 'UploadedFileTypeP1']
        labels = {
            'UploadedFileP1': _('Upload your structure file for "Complex (ML)" molecule'),
            'UploadedFileTypeP1': _('Format'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedFileP1': forms.FileInput(attrs={'required': True}),
        }


class TransToAForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'TransToA']
        labels = {
            'TransToA': _(''),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'TransToA': forms.RadioSelect,
        }



class QueryForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

class paraInputForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'QMSoftware', 'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet',
                  'QMCharge', 'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent',
                  'QMCavitySurface', 'QMScalingFactor',

                  'QMSoftwareP1', 'QMTitleP1', 'QMCalTypeP1', 'QMProcessorsP1', 'QMMemoryP1', 'QMFunctionalP1', 'QMBasisSetP1',
                  'QMChargeP1', 'QMMultiplicityP1', 'QMCoordinateFormatP1', 'QMSolvationModelP1', 'QMSolventP1',
                  'QMCavitySurfaceP1', 'QMScalingFactorP1',

                  'QMSoftwareM', 'QMTitleM', 'QMCalTypeM', 'QMProcessorsM', 'QMMemoryM', 'QMFunctionalM', 'QMBasisSetM',
                  'QMChargeM', 'QMMultiplicityM', 'QMCoordinateFormatM', 'QMSolvationModelM', 'QMSolventM',
                  'QMCavitySurfaceM', 'QMScalingFactorM',

                  ]
        labels = {
            'QMSoftware': _('Software'),
            'QMTitle': _('Title of calculations (optional)'),
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
            'QMTitleP1': _('Title of calculations (optional)'),
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

            'QMSoftwareM': _('Software'),
            'QMTitleM': _('Title of calculations (optional)'),
            'QMCalTypeM': _('Type of calculations'),
            'QMProcessorsM': _('Number of processors (max: 4)'),
            'QMMemoryM': _('Meory to use (unit: GB, max: 2)'),
            'QMFunctionalM': _('Functional'),
            'QMBasisSetM': _('BasisSet'),
            'QMChargeM': _('Charge'),
            'QMMultiplicityM': _('Multiplicity'),
            'QMCoordinateFormatM': _('Format of the coordinates'),
            'QMSolvationModelM': _('Solvation model'),
            'QMSolventM': _('Solvent'),
            'QMCavitySurfaceM': _('Surface type for the cavity'),
            'QMScalingFactorM': _('Scaling factor for the cavity'),

        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),

            # set the default value for the scaling factors.
            'QMScalingFactor': forms.TextInput(attrs={'value': 0.485, 'required': True}),
            'QMScalingFactorP1': forms.TextInput(attrs={'value': 1.000, 'required': True}),
            'QMScalingFactorM': forms.TextInput(attrs={'value': 0.977, 'required': True})
        }


class UploadOutputForm(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedOutputFile']
        labels = {
            'UploadedOutputFile': _('Upload the output file for "Ligand (L-)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedOutputFile': forms.FileInput(attrs={'required': True}),
        }

class UploadOutputFormP1(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedOutputFileP1']
        labels = {
            'UploadedOutputFileP1': _('Upload the output file for "Complex (ML)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedOutputFileP1': forms.FileInput(attrs={'required': True}),
        }

class UploadOutputFormM(ModelForm):
    class Meta:
        model = LogKJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedOutputFileM']
        labels = {
            'UploadedOutputFileM': _('Upload the output file for "Metal (M+)" molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedOutputFileM': forms.FileInput(attrs={'required': True}),
        }
