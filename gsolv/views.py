from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import GSolvJob, UploadForm, QueryForm, SmilesForm, GsolvInputForm
from cyshg.models import AllJobIDs


from scripts.JobManagement import JobManagement
from scripts.VistorStatistics import clientStatistics
import threading
import base64, os

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'gsolv/index.html')

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
            return redirect('/gsolv/parameters/%d' % int(model_instance.JobID))
    else:
        form = UploadForm()

    return render(request, 'gsolv/upload.html', {'form': form})

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
            return redirect('/gsolv/parameters/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()

    return render(request, 'gsolv/smiles.html', {'form': form})

def parameters_input(request, JobID):
    clientStatistics(request)
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
    clientStatistics(request)
    return render(request, 'gsolv/parameters_doc.html')

def review(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(GSolvJob, JobID=JobID)
    return render(request, 'gsolv/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    clientStatistics(request)
    return render(request, 'gsolv/review_doc.html')

def results(request, JobID, JobType='gsolv'):
    clientStatistics(request)
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(GSolvJob, JobID=JobID)

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
        jobmanger.GsolvJobPrepare(obj=item, JobType='gsolv')

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.GSolvJobExec, kwargs={"obj": item})
        #Exec_thread.start()

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
                return render(request, 'gsolv/results_doc.html', {'form': form})

            # find where does the JobID belongs to.
            JobID_query = int(model_instance.JobID)
            alljobs = AllJobIDs.objects.all()
            allJobID = [i.JobID for i in alljobs]
            allJobID_csearch = []
            allJobID_gsolv = []
            allJobID_pka = []
            allJobID_logk = []
            allJobID_hgspeci = []
            for j in alljobs:
                if j.JobType in ['csearch'] or j.SubJobType in ['csearch']:
                    allJobID_csearch.append(j.JobID)
                elif j.JobType in ['gsolv'] or j.SubJobType in ['gsolv']:
                    allJobID_gsolv.append(j.JobID)
                elif j.JobType in ['pka'] or j.SubJobType in ['pka']:
                    allJobID_pka.append(j.JobID)
                elif j.JobType in ['logk'] or j.SubJobType in ['logk']:
                    allJobID_logk.append(j.JobID)
                elif j.JobType in ['hgspeci'] or j.SubJobType in ['hgspeci']:
                    allJobID_hgspeci.append(j.JobID)

            if JobID_query not in allJobID:
                return render(request, 'csearch/results_doc.html', {'form': form})

            if JobID_query in allJobID_csearch:
                return redirect('/csearch/results/%d' % int(model_instance.JobID))
            elif JobID_query in allJobID_gsolv:
                return redirect('/gsolv/results/%d' % int(model_instance.JobID))
            elif JobID_query in allJobID_pka:
                return redirect('/pka/results/%d' % int(model_instance.JobID))
            elif JobID_query in allJobID_logk:
                return redirect('/logk/results/%d' % int(model_instance.JobID))
            elif JobID_query in allJobID_hgspeci:
                return redirect('/hgspeci/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'gsolv/results_doc.html', {'form': form})







def get_job_dir(JobID, JobType='gsolv'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def generate_JobID(module=AllJobIDs, JobType='gsolv'):
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


def results_xyz(request, JobID, Ith, JobType='gsolv'):
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


def inputcoor(request, JobID, JobType='gsolv'):
    """
    convert input files to xyz and show
    """
    clientStatistics(request)
    item = get_object_or_404(GSolvJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType='gsolv')

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def inputfile(request, JobID, JobType='gsolv'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(GSolvJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if item.QMSoftware == 'Gaussian':
        inputfile = '%s/%s-%s.com' % (job_dir, JobType, JobID)
    elif item.QMSoftware == 'NWChem':
        inputfile = '%s/%s-%s.nw' % (job_dir, JobType, JobID)

    fcon = ''.join(open(inputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
