from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
import json

from scripts.VistorStatistics import clientStatistics
from .models import StatisticsData
# Create your views here.


def index(request):
    clientStatistics(request)
    numVist = StatisticsData.objects.count()
    return render(request, 'index.html', {'numVist': numVist})

def faq(request):
    clientStatistics(request)
    return render(request, 'faq.html')

# function for ajax query
def query_statistics(request):
    clientStatistics(request)

    response_dict = {'success': True}
    response_dict['numVist'] = StatisticsData.objects.count()

    return HttpResponse(json.dumps(response_dict))
