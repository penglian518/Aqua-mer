from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import CSearchJob, SmilesForm, UploadForm, SearchTypeForm, RandomSearchForm, QueryForm, ReclusteringForm


from scripts.JobManagement import JobManagement
import threading
import base64, os

# Create your views here.


def index(request):
    return render(request, 'csearch/index.html')

def draw(request):
    return render(request, 'csearch/draw.html')

def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = CSearchJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/csearch/parameters/%d' % int(model_instance.JobID))
    else:
        form = UploadForm()

    return render(request, 'csearch/upload.html', {'form': form})

def smiles(request):
    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lastjobid = CSearchJob.objects.last().id
            except AttributeError:
                lastjobid = 0
            model_instance = form.save(commit=False)
            model_instance.JobID = lastjobid + 1
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/csearch/parameters/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm()

    return render(request, 'csearch/smiles.html', {'form': form})



def parameters_cstype(request, JobID):
    item = get_object_or_404(CSearchJob, JobID=JobID)
    if request.method == 'POST':
        form = SearchTypeForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "2.0"
            model_instance.Successful = True
            model_instance.save()
            if model_instance.CSearchType == 'Random':
                return redirect('/csearch/parameters_random/%d' % int(model_instance.JobID))
            elif model_instance.CSearchType == 'Replica':
                return redirect('/csearch/parameters_replica/%d' % int(model_instance.JobID))
            elif model_instance.CSearchType == 'DFT':
                return redirect('/csearch/parameters_dft/%d' % int(model_instance.JobID))
    else:
        form = SearchTypeForm()
    return render(request, 'csearch/parameters.html', {'form': form, 'JobID': JobID})

def parameters_random(request, JobID):

    item = get_object_or_404(CSearchJob, JobID=JobID)
    if request.method == 'POST':
        form = RandomSearchForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "2.1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/csearch/review/%d' % int(model_instance.JobID))

    else:
        form = RandomSearchForm()
    return render(request, 'csearch/parameters_random.html', {'form': form, 'JobID': JobID})

def parameters_replica(request, JobID):

    return render(request, 'csearch/parameters_replica.html', {'JobID': JobID})

def parameters_dft(request, JobID):

    return render(request, 'csearch/parameters_dft.html', {'JobID': JobID})

def parameters(request):
    return render(request, 'csearch/parameters_doc.html')

def review(request, JobID):
    item = get_object_or_404(CSearchJob, JobID=JobID)
    return render(request, 'csearch/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    return render(request, 'csearch/review_doc.html')


def results(request, JobID, JobType='csearch'):
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(CSearchJob, JobID=JobID)

    if item.CurrentStatus == '0':
        # the job is 'to be start', submit the job and jump to '1'

        # a function to start the job
        #### call some function here ####
        # a. generate input file
        # b. submit the job

        # generate command line file
        jobmanger = JobManagement()
        if item.RandomReclustering:
            jobmanger.CSearchJobReclustering(obj=item)
        else:
            jobmanger.CSearchJobPrepare(obj=item)

        # run the calculations in background
        Exec_thread = threading.Thread(target=jobmanger.JobExec, kwargs={"obj": item, 'JobType':JobType})
        Exec_thread.start()



        # change the status in the database
        item.CurrentStatus = '1'
        item.Successful = True
        item.FailedReason = ''
        item.save()
        # redirect to the result page
        return redirect('/csearch/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'csearch/results_jobrunning.html', {'JobID': JobID, 'Item': item})
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

        return render(request, 'csearch/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'csearch/results_error.html', {'JobID': JobID, 'Item': item})

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
                return render(request, 'csearch/results_doc.html', {'form': form})

            # show the result, if the JobID is available in the system
            return redirect('/csearch/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'csearch/results_doc.html', {'form': form})

def reclustering(request, JobID):
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(CSearchJob, JobID=JobID)

    if item.CurrentStatus == '0':
        # the job is 'to be start', submit the job and jump to '1'

        # change the status in the database
        item.CurrentStatus = '1'
        item.save()
        # redirect to the result page
        return redirect('/csearch/reclustering/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'csearch/results_jobrunning.html', {'JobID': JobID, 'Item': item})
    if item.CurrentStatus == '2':
        # the job is finished.
        if request.method == 'POST':
            form = ReclusteringForm(request.POST, instance=item)
            if form.is_valid():
                model_instance = form.save(commit=False)
                model_instance.JobID = JobID
                model_instance.CurrentStep = "2.1.1"
                model_instance.Successful = True
                model_instance.RandomReclustering = True
                # change the status to "to be start" to run the jobs
                model_instance.CurrentStatus = '0'
                model_instance.save()
                return redirect('/csearch/results/%d' % int(model_instance.JobID))

        else:
            form = ReclusteringForm()
        return render(request, 'csearch/reclustering_para.html', {'form': form, 'JobID': JobID})
    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'csearch/results_error.html', {'JobID': JobID, 'Item': item})


def reclustering_doc(request):

    if request.method == 'POST':
        # user filled form
        form = QueryForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)

            # if the JobID is not valid, go back to the initial state
            try:
                int(model_instance.JobID)
            except:
                return render(request, 'csearch/reclustering_doc.html', {'form': form})

            # show the result, if the JobID is available in the system
            return redirect('/csearch/reclustering/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'csearch/reclustering_doc.html', {'form': form})

def download(request, JobID, JobType='csearch'):
    item = get_object_or_404(CSearchJob, JobID=JobID)

    if item.CurrentStatus == '2':
        # the job is finished, display the results.
        job_dir = get_job_dir(JobID)
        output_zip = '%s/%s-%s.zip' % (job_dir, JobType, JobID)
        if not os.path.exists(output_zip):
            jobmanger = JobManagement()
            jobmanger.Zip4Downlaod(obj=item, JobType=JobType)

        with open(output_zip, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-zip-compressed")
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(output_zip)
            return response

    raise Http404


def get_job_dir(JobID, JobType='csearch'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def results_xyz(request, JobID, Ith, JobType='csearch'):
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

def inputcoor(request, JobID, JobType='csearch'):
    """
    convert input files to xyz and show
    """
    item = get_object_or_404(CSearchJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item)

    # read xyz file
    job_dir = get_job_dir(JobID)
    xyzfile = '%s/%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
