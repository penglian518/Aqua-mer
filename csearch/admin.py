from django.contrib import admin

# Register your models here.

from .models import CSearchJob

class CSearchJobAdmin(admin.ModelAdmin):
    model = CSearchJob

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'CSearchType',
                    'RandomForcefield', 'RandomNRotamers', 'RandomNSteps', 'RandomEPS', 'RandomNMinSamples', 'Note')



admin.site.register(CSearchJob, CSearchJobAdmin)
