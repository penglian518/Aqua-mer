from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
#from .models import CSearchJob, UploadForm, SearchTypeForm, RandomSearchForm, QueryForm, ReclusteringForm


from scripts.JobManagement import JobManagement
import threading
import base64, os

# Create your views here.


def index(request):
    return render(request, 'logk/index.html')
