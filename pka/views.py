from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import pKaJob, UploadForm, QueryForm, SmilesForm, pKaInputForm, UploadFormP1, SmilesFormP1
from cyshg.models import AllJobIDs


from scripts.JobManagement import JobManagement
from scripts.VistorStatistics import clientStatistics
import threading
import base64, os

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'pka/index.html')

def upload(request, Mol):
    clientStatistics(request)
    if Mol in ['Success', 'success']:
        return render(request, 'pka/upload_success.html')

    if request.method == 'POST':
        if Mol in ['A', 'A-']:
            form = UploadForm(request.POST, request.FILES)
        elif Mol in ['HA']:
            form = UploadFormP1(request.POST, request.FILES)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = generate_JobID()
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/pka/upload/success/')
    else:
        if Mol in ['A', 'A-']:
            form = UploadForm()
        elif Mol in ['HA']:
            form = UploadFormP1()

    return render(request, 'pka/upload.html', {'form': form})

def smiles(request):
    clientStatistics(request)
    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES)
        formP1 = SmilesFormP1(request.POST, request.FILES)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = generate_JobID()
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/pka/parameters/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()
        formP1 = SmilesFormP1()

    return render(request, 'pka/smiles.html', {'form': form, 'formP1': formP1})

def parameters_input(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    if request.method == 'POST':
        form = pKaInputForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "2.1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/pka/review/%d' % int(model_instance.JobID))

    else:
        form = pKaInputForm()
    return render(request, 'pka/parameters_input.html', {'form': form, 'JobID': JobID})

def parameters(request):
    clientStatistics(request)
    return render(request, 'pka/parameters_doc.html')

def review(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    return render(request, 'pka/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    clientStatistics(request)
    return render(request, 'pka/review_doc.html')

def results(request, JobID, JobType='pka'):
    clientStatistics(request)
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(pKaJob, JobID=JobID)

    if item.CurrentStatus == '0':
        # the job is 'to be start', submit the job and jump to '1'

        # change the status in the database
        item.CurrentStatus = '1'
        item.save()

        # a function to start the job
        #### call some function here ####
        # a. generate input file
        # b. submit the job
        # generate input file

        jobmanger = JobManagement()
        jobmanger.GsolvJobPrepare(obj=item, JobType='pka')

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.pKaJobExec, kwargs={"obj": item})
        #Exec_thread.start()

        # redirect to the result page
        return redirect('/pka/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'pka/results_jobrunning.html', {'JobID': JobID, 'Item': item})
    if item.CurrentStatus == '2':
        # the job is finished, display the results.
        job_dir = get_job_dir(JobID)
        output_cluster_png = '%s/%s-%s/%s-%s.cluster.png' % (job_dir, JobType, JobID, JobType, JobID)

        # read the figure file
        try:
            fig_in_base64 = "data:image/png;base64,%s" % base64.encodestring(open(output_cluster_png).read())
        except:
            fig_in_base64 = base64.encodestring('Figure is not available.')
            pass

        return render(request, 'pka/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'pka/results_error.html', {'JobID': JobID, 'Item': item})


def results_doc(request):
    clientStatistics(request)
    if request.method == 'POST':
        # user filled form
        form = QueryForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)

            # if the JobID is not valid, go back to the initial state
            try:
                int(model_instance.JobID)
            except:
                return render(request, 'pka/results_doc.html', {'form': form})

            # show the result, if the JobID is available in the system
            return redirect('/pka/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'pka/results_doc.html', {'form': form})







def get_job_dir(JobID, JobType='pka'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def generate_JobID(module=AllJobIDs, JobType='pka'):
    try:
        lastjobid = module.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1

    # register that job
    newjob = module.objects.create()
    newjob.JobID = JobID
    newjob.JobType = JobType
    newjob.save()
    return JobID


def results_xyz(request, JobID, Ith, JobType='pka'):
    """
    :param request:
    :param JobID:
    :param Ith: the ith molecule from top
    :return:
    """
    clientStatistics(request)
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s/xyz/CSearch_%s_%s-%s.xyz' % (job_dir, JobType, JobID, Ith, JobType, JobID)

    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')


def inputcoor(request, JobID, JobType='pka'):
    """
    convert input files to xyz and show
    """
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType='pka')

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def inputfile(request, JobID, JobType='pka'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if item.QMSoftware == 'Gaussian':
        inputfile = '%s/%s-%s.com' % (job_dir, JobType, JobID)
    elif item.QMSoftware == 'NWChem':
        inputfile = '%s/%s-%s.nw' % (job_dir, JobType, JobID)

    fcon = ''.join(open(inputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
