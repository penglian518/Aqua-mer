from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict

from .models import LogKJob, UploadForm, QueryForm, SmilesForm, paraInputForm, UploadFormP1, SmilesFormP1, TransToAForm, MetalForm
from toolkit.models import ToolkitJob
from cyshg.models import AllJobIDs


from scripts.JobManagement import JobManagement
from scripts.VistorStatistics import clientStatistics
import threading
import base64, os, datetime, json

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'logk/index.html')

def start(request):
    clientStatistics(request)
    # delete empty jobs that longer then 2 hours
    for j in LogKJob.objects.filter(CurrentStep=0):
        deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
        if deltaT > 3600 * 2:
            j.delete()

    JobID = generate_JobID()
    # occupy this JobID for 2 hours
    SPJob = LogKJob(JobID=JobID)
    SPJob.save()

    return redirect('/logk/smiles/%d/' % JobID)

def smiles(request, JobID):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = LogKJob.objects.get(JobID=JobID)
    except:
        SPJob = LogKJob(JobID=JobID)

    if request.method == 'POST':
        form = SmilesForm(request.POST, request.FILES, instance=SPJob)
        formP1 = SmilesFormP1(request.POST, request.FILES, instance=SPJob)
        formMetal = MetalForm(request.POST, request.FILES, instance=SPJob)
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
        if formMetal.is_valid():
            model_instance = formMetal.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
        return redirect('/logk/parameters/%d' % int(JobID))
    else:
        form = SmilesForm(instance=SPJob)
        formP1 = SmilesFormP1(instance=SPJob)
        formMetal = MetalForm(instance=SPJob)

    return render(request, 'logk/smiles.html', {'form': form, 'formP1': formP1, 'formMetal': MetalForm, 'JobID': JobID})

def smiles_single(request, JobID, Mol):
    clientStatistics(request)

    # get job handle
    try:
        SPJob = LogKJob.objects.get(JobID=JobID)
    except:
        SPJob = LogKJob(JobID=JobID)

    if request.method == 'POST':
        if Mol in ['A', 'L']:
            form = SmilesForm(request.POST, request.FILES, instance=SPJob)
        elif Mol in ['HA', 'ML']:
            form = SmilesFormP1(request.POST, request.FILES, instance=SPJob)

        formMetal = MetalForm(request.POST, request.FILES, instance=SPJob)

        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
        if formMetal.is_valid():
            model_instance = formMetal.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
        return redirect('/logk/parameters/%d' % int(JobID))
    else:
        if Mol in ['A']:
            form = SmilesForm(instance=SPJob)
        elif Mol in ['HA']:
            form = SmilesFormP1(instance=SPJob)
        formMetal = MetalForm(instance=SPJob)

    return_dict = {'form': form, 'formMetal': MetalForm, 'JobID': JobID, 'Mol': Mol}
    return render(request, 'logk/smiles_single.html', return_dict)

def upload(request, Mol, JobID):
    clientStatistics(request)
    if Mol in ['Success', 'success'] and JobID in ['0', 0]:
        return render(request, 'logk/upload_success.html')

    # get job handle
    try:
        SPJob = LogKJob.objects.get(JobID=JobID)
    except:
        SPJob = LogKJob(JobID=JobID)

    if request.method == 'POST':
        if Mol in ['A', 'A-', 'L', 'L-']:
            form = UploadForm(request.POST, request.FILES, instance=SPJob)
        elif Mol in ['HA', 'ML']:
            form = UploadFormP1(request.POST, request.FILES, instance=SPJob)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/logk/upload/success/0/')
    else:
        if Mol in ['A', 'A-', 'L', 'L-']:
            form = UploadForm(instance=SPJob)
        elif Mol in ['HA', 'ML']:
            form = UploadFormP1(instance=SPJob)

    return render(request, 'logk/upload.html', {'form': form})

def trans2a(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(ToolkitJob, JobID=JobID)

    # get job handle
    try:
        SPJob = LogKJob.objects.get(JobID=JobID)
    except:
        SPJob = LogKJob(JobID=JobID)

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
                return redirect('/logk/smiles_single/%s/%s/' % (JobID, 'HA'))
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
                return redirect('/logk/smiles_single/%s/%s/' % (JobID, 'A'))
            elif model_instance.TransToA in ['None']:
                return redirect('/logk/start/')
    else:
        form = TransToAForm(instance=SPJob)

    return render(request, 'logk/trans2a.html', {'form': form})


def parameters_input(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(LogKJob, JobID=JobID)
    if request.method == 'POST':
        form = paraInputForm(request.POST, instance=item)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "2.1"
            model_instance.Successful = True
            model_instance.save()
            return redirect('/logk/review/%d' % int(model_instance.JobID))

    else:
        form = paraInputForm(instance=item)

    seqences = ['QMSoftware', 'QMTitle', 'QMCalType', 'QMProcessors', 'QMMemory', 'QMFunctional', 'QMBasisSet',
                  'QMCharge', 'QMMultiplicity', 'QMCoordinateFormat', 'QMSolvationModel', 'QMSolvent',
                  'QMCavitySurface', 'QMScalingFactor']

    return render(request, 'logk/parameters_input.html', {'form': form, 'JobID': JobID, 'Fields': seqences})

def parameters(request):
    clientStatistics(request)
    return render(request, 'logk/parameters_doc.html')

def review(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(LogKJob, JobID=JobID)
    return render(request, 'logk/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    clientStatistics(request)
    return render(request, 'logk/review_doc.html')

def results(request, JobID, JobType='logk'):
    clientStatistics(request)
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(LogKJob, JobID=JobID)

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
        jobmanger.LogKJobPrepare(obj=item, JobType='logk')

        # run the calculations in background
        #Exec_thread = threading.Thread(target=jobmanger.LogKJobExec, kwargs={"obj": item})
        #Exec_thread.start()

        # redirect to the result page
        return redirect('/logk/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'logk/results_jobrunning.html', {'JobID': JobID, 'Item': item})
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

        return render(request, 'logk/results.html', {'JobID': JobID, 'Item': item, 'chart': fig_in_base64})
    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'logk/results_error.html', {'JobID': JobID, 'Item': item})


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
                return render(request, 'logk/results_doc.html', {'form': form})

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


    return render(request, 'logk/results_doc.html', {'form': form})





# function for ajax query
def query_coor(request, JobID):
    clientStatistics(request)

    response_dict = {'success': True}
    response_dict['JobID'] = JobID

    obj = get_object_or_404(LogKJob, JobID=JobID)

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
def get_job_dir(JobID, JobType='logk'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def generate_JobID(module=AllJobIDs, JobType='logk'):
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


def results_xyz(request, JobID, Ith, JobType='logk'):
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


def inputcoor(request, JobID, JobType='logk', Mol='A'):
    """
    convert input files to xyz and show
    """
    clientStatistics(request)
    item = get_object_or_404(LogKJob, JobID=JobID)
    # convert smi to xyz
    jobmanger = JobManagement()
    jobmanger.Convert2XYZ(item, JobType='logk')

    # read xyz file
    job_dir = get_job_dir(JobID)

    if Mol in ['L', 'A']:
        xyzfile = '%s/L_%s-%s.xyz' % (job_dir, JobType, JobID)
    elif Mol in ['ML', 'HA']:
        xyzfile = '%s/ML_%s-%s.xyz' % (job_dir, JobType, JobID)
    elif Mol in ['M']:
        xyzfile = '%s/M_%s-%s.xyz' % (job_dir, JobType, JobID)
    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def inputfile(request, JobID, JobType='logk', Mol='A'):
    """
    display the input files
    """
    clientStatistics(request)
    item = get_object_or_404(LogKJob, JobID=JobID)
    # read xyz file
    job_dir = get_job_dir(JobID)

    if Mol in ['L', 'A']:
        if item.QMSoftware == 'Gaussian':
            inputfile = '%s/L_%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftware == 'NWChem':
            inputfile = '%s/L_%s-%s.nw' % (job_dir, JobType, JobID)
    elif Mol in ['ML', 'HA']:
        if item.QMSoftwareP1 == 'Gaussian':
            inputfile = '%s/ML_%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftwareP1 == 'NWChem':
            inputfile = '%s/ML_%s-%s.nw' % (job_dir, JobType, JobID)
    elif Mol in ['M']:
        if item.QMSoftwareM == 'Gaussian':
            inputfile = '%s/M_%s-%s.com' % (job_dir, JobType, JobID)
        elif item.QMSoftwareM == 'NWChem':
            inputfile = '%s/M_%s-%s.nw' % (job_dir, JobType, JobID)

    fcon = ''.join(open(inputfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')
