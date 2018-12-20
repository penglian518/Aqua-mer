from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .models import GSolvJob, UploadForm, QueryForm, SmilesForm, GsolvInputForm, UploadOutputForm, UploadOutputFormP1
from cyshg.models import AllJobIDs
from pka.models import pKaJob
from logk.models import LogKJob


from scripts.JobManagement import JobManagement
from scripts.VistorStatistics import clientStatistics
import base64, os, datetime

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'gsolv/index.html')

def upload(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = GSolvJob.objects.get(JobID=JobID)
    except:
        SPJob = GSolvJob(JobID=JobID)

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/gsolv/parameters/%d/' % int(model_instance.JobID))
    else:
        form = UploadForm(instance=SPJob)

    return render(request, 'gsolv/upload.html', {'form': form, 'JobID': JobID})

def start(request, type='new'):
    clientStatistics(request)
    # delete empty jobs that longer then 2 hours
    for j in GSolvJob.objects.filter(CurrentStep=0):
        deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
        if deltaT > 3600 * 2:
            j.delete()

    JobID = generate_JobID()
    # occupy this JobID for 2 hours
    SPJob = pKaJob(JobID=JobID)
    SPJob.save()

    if type in ['new']:
        return redirect('/gsolv/smiles/%d/' % JobID)
    elif type in ['output']:
        return redirect('/gsolv/calculate/%d/' % JobID)


def smiles(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = GSolvJob.objects.get(JobID=JobID)
    except:
        SPJob = GSolvJob(JobID=JobID)

    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/gsolv/parameters/%d' % int(model_instance.JobID))
    else:
        form = SmilesForm(instance=SPJob)

    return render(request, 'gsolv/smiles.html', {'form': form, 'JobID': JobID})

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
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(GSolvJob, JobID=JobID)

    if item.CurrentStatus == '0':
        clientStatistics(request)
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
        if JobType in ['gsolv']:
            jobmanger.GsolvJobPrepare(obj=item, JobType=JobType)
        elif JobType in ['gsolv_output']:
            jobmanger.GsolvCollectResults(obj=item, JobType=JobType)

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.GSolvJobExec, kwargs={"obj": item})
        #Exec_thread.start()

        # redirect to the result page
        return redirect('/gsolv/results/%d/%s/' % (int(item.JobID), JobType))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'gsolv/results_jobrunning.html', {'JobID': JobID, 'Item': item})
    if item.CurrentStatus == '2':
        clientStatistics(request)
        # the job is finished, display the results.
        job_dir = get_job_dir(JobID)
        output_cluster_png = '%s/%s-%s/%s-%s.cluster.png' % (job_dir, JobType, JobID, JobType, JobID)

        # read the figure file
        try:
            fig_in_base64 = "data:image/png;base64,%s" % base64.encodestring(open(output_cluster_png).read())
        except:
            fig_in_base64 = base64.encodestring('Figure is not available.')
            pass

        if JobType in ['gsolv']:
            return render(request, 'gsolv/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
        elif JobType in ['gsolv_output']:
            return render(request, 'gsolv/results_output.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})

    if item.CurrentStatus == '3':
        clientStatistics(request)
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
                item = get_object_or_404(GSolvJob, JobID=JobID_query)
                if float(item.CurrentStep) > 3:
                    return redirect('/gsolv/results/%d/gsolv_output/' % int(model_instance.JobID))
                else:
                    return redirect('/gsolv/results/%d/gsolv/' % int(model_instance.JobID))
            elif JobID_query in allJobID_pka:
                item = get_object_or_404(pKaJob, JobID=JobID_query)
                if float(item.CurrentStep) > 3:
                    return redirect('/pka/results/%d/pka_output/' % int(model_instance.JobID))
                else:
                    return redirect('/pka/results/%d/pka/' % int(model_instance.JobID))
            elif JobID_query in allJobID_logk:
                item = get_object_or_404(LogKJob, JobID=JobID_query)
                if float(item.CurrentStep) > 3:
                    return redirect('/logk/results/%d/logk_output/' % int(model_instance.JobID))
                else:
                    return redirect('/logk/results/%d/logk/' % int(model_instance.JobID))
            elif JobID_query in allJobID_hgspeci:
                return redirect('/hgspeci/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'gsolv/results_doc.html', {'form': form})

def calculate(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = GSolvJob.objects.get(JobID=JobID)
    except:
        SPJob = GSolvJob(JobID=JobID)

    if request.method == 'POST':
        form = UploadOutputForm(request.POST, request.FILES, instance=SPJob)
        formP1 = UploadOutputFormP1(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "5"
            model_instance.Successful = True
            model_instance.save()
        if formP1.is_valid():
            model_instance = formP1.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "5"
            model_instance.Successful = True
            model_instance.save()
        return redirect('/gsolv/results/%d/%s/' % (int(JobID), 'gsolv_output'))
    else:
        form = UploadOutputForm(instance=SPJob)
        formP1 = UploadOutputFormP1(instance=SPJob)

    return render(request, 'gsolv/calculate.html', {'form': form, 'formP1': formP1, 'JobID': JobID})






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

    if JobType in ['gsolv']:
        if item.QMSoftware == 'Gaussian':
            inputfile = '%s/%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftware == 'NWChem':
            inputfile = '%s/%s-%s.nw' % (job_dir, JobType, JobID)
    elif JobType in ['gsolv_gas']:
        if item.QMSoftware == 'Gaussian':
            inputfile = '%s/gsolv-%s_gas.com' % (job_dir, JobID)
        elif item.QMSoftware == 'NWChem':
            inputfile = '%s/gsolv-%s_gas.nw' % (job_dir, JobID)

    fcon = ''.join(open(inputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def outputfile(request, JobID, JobType='gsolv',  Mol='aq'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(GSolvJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if Mol in ['aq']:
        outputfile = item.UploadedOutputFile.file.name
    elif Mol in ['gas']:
        outputfile = item.UploadedOutputFileP1.file.name

    fcon = ''.join(open(outputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
