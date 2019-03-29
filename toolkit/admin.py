from django.contrib import admin

# Register your models here.
from .models import ToolkitJob


class ToolkitJobAdmin(admin.ModelAdmin):
    model = ToolkitJob

    list_display = ('id', 'JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'Note')

admin.site.register(ToolkitJob, ToolkitJobAdmin)
