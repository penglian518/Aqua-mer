from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import ToolkitJob, CSearchJob, SmilesForm, UploadForm, CalculationTypeForm


from scripts.JobManagement import JobManagement
import threading
import base64, os

# Create your views here.



def index(request):
    return render(request, 'toolkit/index.html')


def draw(request):
    return render(request, 'toolkit/draw.html')

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = ToolkitJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/toolkit/reviewcoors/%d' % int(model_instance.JobID))
    else:
        form = UploadForm()

    return render(request, 'toolkit/upload.html', {'form': form})

def smiles(request):
    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = ToolkitJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/toolkit/reviewcoors/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()

    return render(request, 'toolkit/smiles.html', {'form': form})


def reviewcoors(request, JobID):
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
                return redirect('/csearch/')
            elif model_instance.Name == 'gsolv':
                return redirect('/gsolv/')
            elif model_instance.Name == 'pka':
                return redirect('/pka/')
            elif model_instance.Name == 'logk':
                return redirect('/logk/')
    else:
        form = CalculationTypeForm()

    return render(request, 'toolkit/reviewcoors.html', {'JobID': JobID, 'Item': item, 'form': form})





def get_job_dir(JobID, JobType='toolkit'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def inputcoor(request, JobID, JobType='toolkit'):
    """
    convert input files to xyz and show
    """
    item = get_object_or_404(ToolkitJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType=JobType)

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
