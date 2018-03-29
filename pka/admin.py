from django.contrib import admin

from .models import pKaJob
# Register your models here.

class pKaJobAdmin(admin.ModelAdmin):
    model = pKaJob

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate', 'FromToolkitToA',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'QMSoftware',
                    'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet', 'QMCharge',
                    'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent', 'QMCavitySurface', 'QMScalingFactor', 'Note',
                    'SmilesStrP1', 'UploadedFileP1', 'UploadedFileTypeP1', 'QMSoftwareP1',
                    'QMTitleP1', 'QMCalTypeP1', 'QMProcessorsP1', 'QMMemoryP1', 'QMFunctionalP1', 'QMBasisSetP1', 'QMChargeP1',
                    'QMMultiplicityP1', 'QMCoordinateFormatP1', 'QMSolvationModelP1', 'QMSolventP1', 'QMCavitySurfaceP1', 'QMScalingFactorP1', 'NoteP1',
                    )

admin.site.register(pKaJob, pKaJobAdmin)
