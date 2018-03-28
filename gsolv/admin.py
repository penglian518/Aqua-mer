from django.contrib import admin

from .models import GSolvJob
# Register your models here.

class GSolvJobAdmin(admin.ModelAdmin):
    model = GSolvJob

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'QMSoftware',
                    'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet', 'QMCharge',
                    'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent', 'QMCavitySurface', 'QMScalingFactor', 'Note')

admin.site.register(GSolvJob, GSolvJobAdmin)
