from django.contrib import admin

# Register your models here.
from .models import ToolkitJob, CSearchJob

class CSearchJobInline(admin.TabularInline):
    model = CSearchJob
    extra = 1

class CSearchJobAdmin(admin.ModelAdmin):
    model = CSearchJob
    list_display = ('CSearchJobID', 'CSearchType', 'RandomForcefield', 'RandomNRotamers', 'RandomNSteps', 'RandomEPS', 'RandomNMinSamples',)





class ToolkitJobAdmin(admin.ModelAdmin):
    model = ToolkitJob
    inlines = [
        CSearchJobInline,
    ]

    list_display = ('JobID', 'Name', 'CurrentStep', 'CurrentStatus', 'Successful', 'FailedReason', 'CreatedDate',
                    'SmilesStr', 'UploadedFile', 'UploadedFileType', 'Note')

admin.site.register(ToolkitJob, ToolkitJobAdmin)
admin.site.register(CSearchJob, CSearchJobAdmin)
