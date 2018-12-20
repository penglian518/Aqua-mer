from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict

from .models import pKaJob, UploadForm, QueryForm, SmilesForm, pKaInputForm, UploadFormP1, SmilesFormP1, TransToAForm, UploadOutputForm, UploadOutputFormP1
from toolkit.models import ToolkitJob
from cyshg.models import AllJobIDs
from logk.models import LogKJob
from gsolv.models import GSolvJob

from scripts.JobManagement import JobManagement
from scripts.VistorStatistics import clientStatistics
import threading
import base64, os, datetime, json

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'pka/index.html')

def start(request, type='new'):
    clientStatistics(request)
    # delete empty jobs that longer then 2 hours
    for j in pKaJob.objects.filter(CurrentStep=0):
        deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
        if deltaT > 3600 * 2:
            j.delete()

    JobID = generate_JobID()
    # occupy this JobID for 2 hours
    SPJob = pKaJob(JobID=JobID)
    SPJob.save()

    if type in ['new']:
        return redirect('/pka/smiles/%d/' % JobID)
    elif type in ['output']:
        return redirect('/pka/calculate/%d/' % JobID)

def smiles(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = pKaJob.objects.get(JobID=JobID)
    except:
        SPJob = pKaJob(JobID=JobID)

    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES, instance=SPJob)
        formP1 = SmilesFormP1(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
        if formP1.is_valid():
            model_instance = formP1.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
        return redirect('/pka/parameters/%d' % int(JobID))
    else:
        form = SmilesForm(instance=SPJob)
        formP1 = SmilesFormP1(instance=SPJob)

    return render(request, 'pka/smiles.html', {'form': form, 'formP1': formP1, 'JobID': JobID})

def smiles_single(request, JobID, Mol):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = pKaJob.objects.get(JobID=JobID)
    except:
        SPJob = pKaJob(JobID=JobID)

    if request.method == 'POST':
        if Mol in ['A']:
            form = SmilesForm(request.POST, request.FILES, instance=SPJob)
        elif Mol in ['HA']:
            form = SmilesFormP1(request.POST, request.FILES, instance=SPJob)

        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/pka/parameters/%d' % int(JobID))
    else:
        if Mol in ['A']:
            form = SmilesForm(instance=SPJob)
        elif Mol in ['HA']:
            form = SmilesFormP1(instance=SPJob)

    return_dict = {'form': form, 'JobID': JobID, 'Mol': Mol}
    return render(request, 'pka/smiles_single.html', return_dict)

def upload(request, Mol, JobID):
    clientStatistics(request)
    if Mol in ['Success', 'success'] and JobID in ['0', 0]:
        return render(request, 'pka/upload_success.html')

    # get job handle
    try:
        SPJob = pKaJob.objects.get(JobID=JobID)
    except:
        SPJob = pKaJob(JobID=JobID)

    if request.method == 'POST':
        if Mol in ['A', 'A-']:
            form = UploadForm(request.POST, request.FILES, instance=SPJob)
        elif Mol in ['HA']:
            form = UploadFormP1(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/pka/upload/success/0/')
    else:
        if Mol in ['A', 'A-']:
            form = UploadForm(instance=SPJob)
        elif Mol in ['HA']:
            form = UploadFormP1(instance=SPJob)

    return render(request, 'pka/upload.html', {'form': form})

def trans2a(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(ToolkitJob, JobID=JobID)

    # get job handle
    try:
        SPJob = pKaJob.objects.get(JobID=JobID)
    except:
        SPJob = pKaJob(JobID=JobID)

    if request.method == 'POST':
        form = TransToAForm(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            if model_instance.TransToA in ['A']:
                # copy the data to A
                model_instance.CurrentStep = item.CurrentStep
                model_instance.CurrentStatus = item.CurrentStatus
                model_instance.Name = item.Name
                model_instance.Successful = item.Successful
                model_instance.FailedReason = item.FailedReason

                model_instance.SmilesStr = item.SmilesStr
                model_instance.UploadedFile = item.UploadedFile
                model_instance.UploadedFileType = item.UploadedFileType
                model_instance.Note = item.Note

                model_instance.save()

                #return HttpResponse('upload HA')
                return redirect('/pka/smiles_single/%s/%s/' % (JobID, 'HA'))
            elif model_instance.TransToA in ['HA']:
                # copy the data to HA
                model_instance.CurrentStep = item.CurrentStep
                model_instance.CurrentStatus = item.CurrentStatus
                model_instance.Name = item.Name
                model_instance.Successful = item.Successful
                model_instance.FailedReason = item.FailedReason

                model_instance.SmilesStrP1 = item.SmilesStr
                model_instance.UploadedFileP1 = item.UploadedFile
                model_instance.UploadedFileTypeP1 = item.UploadedFileType
                model_instance.NoteP1 = item.Note

                model_instance.save()
                #return HttpResponse('upload A-')
                return redirect('/pka/smiles_single/%s/%s/' % (JobID, 'A'))
            elif model_instance.TransToA in ['None']:
                return redirect('/pka/start/new/')
    else:
        form = TransToAForm(instance=SPJob)

    return render(request, 'pka/trans2a.html', {'form': form})


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
        form = pKaInputForm(instance=item)

    seqences = ['QMSoftware', 'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet',
                  'QMCharge', 'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent',
                  'QMCavitySurface', 'QMScalingFactor']

    return render(request, 'pka/parameters_input.html', {'form': form, 'JobID': JobID, 'Fields': seqences})

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
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(pKaJob, JobID=JobID)

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
        if JobType in ['pka']:
            jobmanger.pKaJobPrepare(obj=item, JobType=JobType)
        elif JobType in ['pka_output']:
            jobmanger.pKaCollectResults(obj=item, JobType=JobType)

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.pKaJobExec, kwargs={"obj": item})
        #Exec_thread.start()

        # redirect to the result page
        return redirect('/pka/results/%d/%s/' % (int(item.JobID), JobType))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'pka/results_jobrunning.html', {'JobID': JobID, 'Item': item})
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
        if JobType in ['pka']:
            return render(request, 'pka/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
        elif JobType in ['pka_output']:
            return render(request, 'pka/results_output.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})

    if item.CurrentStatus == '3':
        clientStatistics(request)
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


    return render(request, 'pka/results_doc.html', {'form': form})

def calculate(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = pKaJob.objects.get(JobID=JobID)
    except:
        SPJob = pKaJob(JobID=JobID)

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
        return redirect('/pka/results/%d/%s/' % (int(JobID), 'pka_output'))
    else:
        form = UploadOutputForm(instance=SPJob)
        formP1 = UploadOutputFormP1(instance=SPJob)

    return render(request, 'pka/calculate.html', {'form': form, 'formP1': formP1, 'JobID': JobID})




# function for ajax query
def query_coor(request, JobID):
    clientStatistics(request)

    response_dict = {'success': True}
    response_dict['JobID'] = JobID

    obj = get_object_or_404(pKaJob, JobID=JobID)

    HasA = False
    HasHA = False

    if obj.UploadedFile:
        HasA = True

    if obj.UploadedFileP1:
        HasHA = True

    response_dict['HasA'] = HasA
    response_dict['HasHA'] = HasHA

    #return render(request, 'hgspeci/solutionmaster.html', response_dict)
    return HttpResponse(json.dumps(response_dict))

# public functions
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


def inputcoor(request, JobID, JobType='pka', Mol='A'):
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

    if Mol in ['A']:
        xyzfile = '%s/A_%s-%s.xyz' % (job_dir, JobType, JobID)
    elif Mol in ['HA']:
        xyzfile = '%s/HA_%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def inputfile(request, JobID, JobType='pka', Mol='A'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if Mol in ['A']:
        if item.QMSoftware == 'Gaussian':
            inputfile = '%s/A_%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftware == 'NWChem':
            inputfile = '%s/A_%s-%s.nw' % (job_dir, JobType, JobID)
    elif Mol in ['HA']:
        if item.QMSoftwareP1 == 'Gaussian':
            inputfile = '%s/HA_%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftwareP1 == 'NWChem':
            inputfile = '%s/HA_%s-%s.nw' % (job_dir, JobType, JobID)

    fcon = ''.join(open(inputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def outputfile(request, JobID, JobType='pka', Mol='A'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(pKaJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if Mol in ['A']:
        outputfile = item.UploadedOutputFile.file.name
    elif Mol in ['HA']:
        outputfile = item.UploadedOutputFileP1.file.name

    fcon = ''.join(open(outputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
