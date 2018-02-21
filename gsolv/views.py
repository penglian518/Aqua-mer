from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import GSolvJob, UploadForm, QueryForm, SmilesForm, GsolvInputForm


from scripts.JobManagement import JobManagement
import threading
import base64, os

# Create your views here.


def index(request):
    return render(request, 'gsolv/index.html')

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = GSolvJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/gsolv/parameters/%d' % int(model_instance.JobID))
    else:
        form = UploadForm()

    return render(request, 'gsolv/upload.html', {'form': form})

def smiles(request):
    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = GSolvJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/gsolv/parameters/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()

    return render(request, 'gsolv/smiles.html', {'form': form})

def parameters_input(request, JobID):

    item = get_object_or_404(GSolvJob, JobID=JobID)
    if request.method == 'POST':
        form = GsolvInputForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "2.1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/gsolv/review/%d' % int(model_instance.JobID))

    else:
        form = GsolvInputForm()
    return render(request, 'gsolv/parameters_input.html', {'form': form, 'JobID': JobID})

def parameters(request):
    return render(request, 'gsolv/parameters_doc.html')

def review(request, JobID):
    item = get_object_or_404(GSolvJob, JobID=JobID)
    return render(request, 'gsolv/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    return render(request, 'gsolv/review_doc.html')

def results(request, JobID, JobType='gsolv'):
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(GSolvJob, JobID=JobID)

    if item.CurrentStatus == '0':
        # the job is 'to be start', submit the job and jump to '1'

        # a function to start the job
        #### call some function here ####
        # a. generate input file
        # b. submit the job

        # generate input file
        jobmanger = JobManagement()

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.GSolvJobExec, kwargs={"obj": item})
        #Exec_thread.start()



        # change the status in the database
        item.CurrentStatus = '1'
        item.save()
        # redirect to the result page
        return redirect('/gsolv/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'gsolv/results_jobrunning.html', {'JobID': JobID, 'Item': item})
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

        return render(request, 'gsolv/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'gsolv/results_error.html', {'JobID': JobID, 'Item': item})


def results_doc(request):

    if request.method == 'POST':
        # user filled form
        form = QueryForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)

            # if the JobID is not valid, go back to the initial state
            try:
                int(model_instance.JobID)
            except:
                return render(request, 'gsolv/results_doc.html', {'form': form})

            # show the result, if the JobID is available in the system
            return redirect('/gsolv/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'gsolv/results_doc.html', {'form': form})







def get_job_dir(JobID, JobType='gsolv'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def results_xyz(request, JobID, Ith, JobType='gsolv'):
    """

    :param request:
    :param JobID:
    :param Ith: the ith molecule from top
    :return:
    """

    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s/xyz/CSearch_%s_%s-%s.xyz' % (job_dir, JobType, JobID, Ith, JobType, JobID)

    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')


def inputcoor(request, JobID, JobType='gsolv'):
    """
    convert input files to xyz and show
    """
    item = get_object_or_404(GSolvJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType='gsolv')

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
