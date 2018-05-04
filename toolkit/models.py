from __future__ import unicode_literals

from django.db import models
from django import forms
from django.forms import ModelForm
from datetime import datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _

# Create your models here.
def user_directory_path(instance, filename):
    # upload to MEDIA_ROOT/csearch/jobs/JOB_ID/
    return 'toolkit/jobs/{0}/{1}'.format(instance.JobID, filename)

@python_2_unicode_compatible  # only if you need to support Python 2
class ToolkitJob(models.Model):
    CalculationTypes = (
        ('csearch', 'Conformational search'),
        ('gsolv', 'Solvation free energy calculation'),
        ('pka', 'pKa calculation'),
        ('logk', 'log K calculation'),
    )

    FileTypes = (
        ('xyz', 'xyz'),
        ('pdb', 'pdb'),
        ('sdf', 'sdf'),
        ('mol2', 'mol2'),
    )


    JobStatus = (
        ('0', 'to be start'),
        ('1', 'running'),
        ('2', 'finished'),
        ('3', 'something wrong'),
    )


    JobID = models.PositiveIntegerField(blank=True, default=0)
    # calculation type
    Name = models.CharField(max_length=50, choices=CalculationTypes, default='')
    CurrentStep = models.CharField(max_length=10, blank=True, default='0')
    CurrentStatus = models.CharField(max_length=10, choices=JobStatus, default='0')
    Successful = models.BooleanField(default=False)
    FailedReason = models.CharField(max_length=100, blank=True, default='')
    CreatedDate = models.DateTimeField('date created', default=datetime.now())

    SmilesStr = models.CharField(max_length=200, blank=True, default='', null=True)
    UploadedFile = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    UploadedFileType = models.CharField(max_length=10, choices=FileTypes, default='')

    Note = models.CharField(max_length=100, blank=True, default='')


    def __str__(self):
        return str(self.pk)

class SmilesForm(ModelForm):
    class Meta:
        model = ToolkitJob
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
        model = ToolkitJob
        fields = ['JobID', 'CurrentStep', 'Successful', 'UploadedFile', 'UploadedFileType']
        labels = {
            'UploadedFile': _('Upload your structure file'),
            'UploadedFileType': _('Format'),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'UploadedFile': forms.FileInput(attrs={'required':True}),
        }

class CalculationTypeForm(ModelForm):
    class Meta:
        model = ToolkitJob

        fields = ['JobID', 'CurrentStep', 'Successful', 'Name']
        labels = {
            'Name': _(''),
        }
        widgets = {
            'JobID': forms.HiddenInput(),
            'CurrentStep': forms.HiddenInput(),
            'Successful': forms.HiddenInput(),
            'Name': forms.RadioSelect,
        }


