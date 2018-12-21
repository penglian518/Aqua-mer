from django.contrib import admin

# Register your models here.
from .models import AllJobIDs, StatisticsData


class AllJobIDsAdmin(admin.ModelAdmin):
    model = AllJobIDs
    list_display = ('JobID', 'JobType', 'SubJobType', 'CPUs', 'CurrentStatus', 'CreatedDate')

class StatisticsDataAdmin(admin.ModelAdmin):
    model = StatisticsData
    list_display = ('IP', 'IPType', 'PagesVisted', 'Date')



admin.site.register(AllJobIDs, AllJobIDsAdmin)
admin.site.register(StatisticsData, StatisticsDataAdmin)
