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
    return 'csearch/jobs/{0}/{1}'.format(instance.JobID, filename)

@python_2_unicode_compatible  # only if you need to support Python 2
class CSearchJob(models.Model):

    CSearchTypes = (
        ('Random', 'Random sampling'),
        ('DFT', 'Random sampling with DFT optimizer'),
        ('Replica', 'Replica exchange sampling'),
    )

    SolvationTypes = (
        ('gas', 'Gas phase'),
        ('wat', 'Explicit water'),
        ('gbis', 'Implicit water (GBIS)'),
    )

    FileTypes = (
        ('xyz', 'xyz'),
        ('pdb', 'pdb'),
        ('sdf', 'sdf'),
        ('mol2', 'mol2'),
    )

    ForcefieldTypes = (
        ('UFF', 'UFF'),
        ('GAFF', 'GAFF'),
        ('Ghemical', 'Ghemical'),
        ('MMFF94', 'MMFF94'),
        ('MMFF94s', 'MMFF94s'),
    )

    XCs = (
        ('PBE', 'PBE'),
        ('LDA', 'LDA'),
    )

    MPMethods = (
        ('PM7', 'PM7'),
        ('PM6', 'PM6'),
        ('RM1', 'RM1'),
        ('PM3', 'PM3'),
        ('AM1', 'AM1'),
        ('MNDO', 'MNDO'),
    )


    JobStatus = (
        ('0', 'to be start'),
        ('1', 'running'),
        ('2', 'finished'),
        ('3', 'something wrong'),
    )


    JobID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=50, blank=True, default='csearch')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField('date created', default=datetime.now())

    SmilesStr = models.CharField(max_length=200, blank=True, default='')
    UploadedFile = models.FileField(upload_to=user_directory_path, blank=True)
    UploadedFileType = models.CharField(max_length=10, choices=FileTypes, default='')

    CSearchType = models.CharField(max_length=30, choices=CSearchTypes, default='Random')

    RandomForcefield = models.CharField(max_length=30, choices=ForcefieldTypes, default='UFF')
    RandomNRotamers = models.PositiveIntegerField(blank=True, default=1000)
    RandomNSteps = models.PositiveIntegerField(blank=True, default=2500)
    RandomEPS = models.FloatField(blank=True, default=0.01)
    RandomNMinSamples = models.PositiveIntegerField(blank=True, default=2)
    RandomReclustering = models.BooleanField(default=False)

    # used by cp2k
    DFTProcessors = models.PositiveIntegerField(blank=True, default=16, validators=[MaxValueValidator(28), MinValueValidator(1)])
    DFTXC = models.CharField(max_length=30, choices=XCs, default='PBE')
    DFTSteps = models.PositiveIntegerField(blank=True, default=200)
    DFTVacuum = models.FloatField(blank=True, default=2.0)
    DFTCharge = models.IntegerField(blank=True, default=0)
    DFTOpenshell = models.BooleanField(default=False)
    DFTCutoff = models.FloatField(blank=True, default=350)
    DFTFmax = models.FloatField(blank=True, default=0.1)

    # used by MOPAC2016
    MPProcessors = models.PositiveIntegerField(blank=True, default=4, validators=[MaxValueValidator(28), MinValueValidator(1)])
    MPMethod = models.CharField(max_length=10, choices=MPMethods, default='PM7')
    MPSteps = models.PositiveIntegerField(blank=True, default=300)
    MPCharge = models.IntegerField(blank=True, default=0)
    MPOpenshell = models.BooleanField(default=False)
    MPFmax = models.FloatField(blank=True, default=0.01)

    ReplicaSolvationType = models.CharField(max_length=30, choices=SolvationTypes, default='wat')
    ReplicaProcessors = models.PositiveIntegerField(blank=True, default=10, validators=[MaxValueValidator(28), MinValueValidator(1)])
    ReplicaNReplicas = models.PositiveIntegerField(blank=True, default=5, validators=[MaxValueValidator(28), MinValueValidator(1)])
    ReplicaNClusters = models.PositiveIntegerField(blank=True, default=5, validators=[MaxValueValidator(28), MinValueValidator(1)])
    ReplicaClusterCutoff = models.FloatField(blank=True, default=1.00)


    Note = models.CharField(max_length=100, blank=True, default='')


    def __str__(self):
        return str(self.pk)


class SmilesForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'SmilesStr']
        labels = {
            'SmilesStr': _('Provide the SMILES of your molecule'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'SmilesStr': forms.TextInput(attrs={'placeholder': 'Paste the SMILES here', 'size': 80, 'required': True})
        }

class UploadForm(ModelForm):
    class Meta:
        model = CSearchJob
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

class SearchTypeForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'CSearchType']
        labels = {
            'CSearchType': _('Which conformational search method do you want to use?'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'CSearchType': forms.RadioSelect,
        }

class RandomSearchForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'RandomForcefield', 'RandomNRotamers', 'RandomNSteps', 'RandomEPS', 'RandomNMinSamples']
        labels = {
            'RandomForcefield': _('Forcefield used for minimization'),
            'RandomNRotamers': _('Total number of rotamers to generate'),
            'RandomNSteps': _('Max minimization steps for each rotamer'),
            'RandomEPS': _('eps value used by DBScan clustering'),
            'RandomNMinSamples': _('Minimum number of samples allowed for a cluster'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }

class ReclusteringForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'RandomReclustering',
                  'RandomEPS', 'RandomNMinSamples']
        labels = {
            'RandomEPS': _('eps value used by DBScan clustering'),
            'RandomNMinSamples': _('Minimum number of samples allowed for a cluster'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'RandomReclustering': forms.HiddenInput(),
        }


class QueryForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID']
        labels = {
            'JobID': _('Job ID'),

        }

class DFTSearchForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'RandomNRotamers', 'DFTProcessors', 'DFTXC', 'DFTCutoff', 'DFTVacuum', 'DFTCharge',
                  'DFTOpenshell', 'DFTSteps', 'DFTFmax', 'RandomEPS', 'RandomNMinSamples']
        labels = {
            'RandomNRotamers': _('Total number of rotamers to generate'),

            'DFTProcessors': _('Number of processors to use. Max 28'),
            'DFTXC': _('Exchange-correlation functional for DFT calculation.'),
            'DFTCutoff': _('Cutoff value of the potential for DFT calculation (Unit Ryd)'),
            'DFTVacuum': _('Vacuum space of the simulation box.'),
            'DFTCharge': _('Charge of the system.'),
            'DFTOpenshell': _('The system has odd number of electron or not.'),
            'DFTSteps': _('Maximum number of optimization steps for each structure.'),
            'DFTFmax': _('Maximum force of the optimized structure.'),

            'RandomEPS': _('eps value used by DBScan clustering'),
            'RandomNMinSamples': _('Minimum number of samples allowed for a cluster'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }


class MPSearchForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'RandomNRotamers', 'MPProcessors', 'MPMethod', 'MPSteps', 'MPCharge',
                  'MPOpenshell', 'MPFmax', 'RandomEPS', 'RandomNMinSamples']
        labels = {
            'RandomNRotamers': _('Total number of rotamers to generate'),

            'MPProcessors': _('Number of processors to use. Max 28'),
            'MPMethod': _('Semi-empirical quantum chemistry method for the calculation.'),
            'MPCharge': _('Charge of the system.'),
            'MPOpenshell': _('The system has odd number of electron or not.'),
            'MPSteps': _('Maximum number of optimization steps for each structure.'),
            'MPFmax': _('Maximum force of the optimized structure.'),

            'RandomEPS': _('eps value used by DBScan clustering'),
            'RandomNMinSamples': _('Minimum number of samples allowed for a cluster'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }




class ReplicaSearchForm(ModelForm):
    class Meta:
        model = CSearchJob
        fields = ['JobID', 'CurrentStep', 'Successful',
                  'ReplicaSolvationType', 'ReplicaProcessors', 'ReplicaNReplicas', 'ReplicaNClusters', 'ReplicaClusterCutoff']
        labels = {
            'ReplicaSolvationType': _('Solvation environment to use (default: water)'),
            'ReplicaProcessors': _('Number of processors to use (Integer times of replicas. Max 28)'),
            'ReplicaNReplicas': _('Number of replicas.'),
            'ReplicaNClusters': _('Number of clusters to generate.'),
            'ReplicaClusterCutoff': _('Threshold for clustering analysis (default 1.0 Angstrom)'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
        }
