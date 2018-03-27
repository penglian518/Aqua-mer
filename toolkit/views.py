from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict

from .models import ToolkitJob, SmilesForm, UploadForm, CalculationTypeForm
from csearch.models import CSearchJob
from gsolv.models import GSolvJob
from cyshg.models import AllJobIDs

from scripts.JobManagement import JobManagement
import threading
import base64, os

from scripts.VistorStatistics import clientStatistics

# Create your views here.



def index(request):
    clientStatistics(request)
    return render(request, 'toolkit/index.html')


def draw(request):
    clientStatistics(request)
    return render(request, 'toolkit/draw.html')

def upload(request):
    clientStatistics(request)
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = generate_JobID()
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/toolkit/reviewcoors/%d' % int(model_instance.JobID))
    else:
        form = UploadForm()

    return render(request, 'toolkit/upload.html', {'form': form})

def smiles(request):
    clientStatistics(request)
    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = generate_JobID()
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/toolkit/reviewcoors/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()

    return render(request, 'toolkit/smiles.html', {'form': form})


def reviewcoors(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(ToolkitJob, JobID=JobID)
    if request.method == 'POST':
        form = CalculationTypeForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1.1"
            model_instance.Successful = True
            model_instance.save()
            if model_instance.Name == 'csearch':
                return redirect('/toolkit/trans/csearch/%s/' % JobID)
            elif model_instance.Name == 'gsolv':
                return redirect('/toolkit/trans/gsolv/%s/' % JobID)
            elif model_instance.Name == 'pka':
                return redirect('/pka/')
            elif model_instance.Name == 'logk':
                return redirect('/logk/')
    else:
        form = CalculationTypeForm()

    return render(request, 'toolkit/reviewcoors.html', {'JobID': JobID, 'Item': item, 'form': form})


def trans(request, JobType, JobID):
    clientStatistics(request)
    '''to transfer the job from toolkit to other modules'''
    item = get_object_or_404(ToolkitJob, JobID=JobID)
    item_dict = model_to_dict(item)

    # copy the job infor to the module
    if JobType in ['csearch']:
        CSearchJob.objects.update_or_create(**item_dict)
    elif JobType in ['gsolv']:
        GSolvJob.objects.update_or_create(**item_dict)

    return redirect('/%s/parameters/%s/' % (JobType, JobID))



def get_job_dir(JobID, JobType='toolkit'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def generate_JobID(module=AllJobIDs):
    try:
        lastjobid = module.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1

    # register that job
    newjob = module.objects.create()
    newjob.JobID = JobID
    newjob.JobType = 'toolkit'
    newjob.save()

    return JobID

def inputcoor(request, JobID, JobType='toolkit'):
    """
    convert input files to xyz and show
    """
    clientStatistics(request)
    item = get_object_or_404(ToolkitJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType=JobType)

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
