from django.contrib import admin

from .models import GSolvJob
# Register your models here.

class GSolvJobAdmin(admin.ModelAdmin):
    model = GSolvJob

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'QMSoftware',
                    'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet', 'QMCharge',
                    'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent', 'QMCavitySurface', 'QMScalingFactor', 'Note',
                    'UploadedOutputFile', 'QMSoftwareOutput', 'EnergyfromOutputFiles', 'UploadedOutputFileP1',
                    'QMSoftwareOutputP1', 'EnergyfromOutputFilesP1', 'GsolvCorrected',

                    )

admin.site.register(GSolvJob, GSolvJobAdmin)
