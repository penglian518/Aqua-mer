from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory
from .models import HgSpeciJob, SPElements, SPElementsForm, ParameterForm
from .models import SPMasterSpecies, SPMasterSpeciesForm, SPSolutionSpecies, SPSolutionSpeciesForm, QueryForm
from phreeqcdb.models import SolutionMasterSpecies, SolutionSpecies

from scripts.JobManagement import JobManagement
import threading
import base64, os, datetime
import pandas as pd
import numpy as np
from decimal import Decimal

# Create your views here.


def index(request):
    return render(request, 'hgspeci/index.html')


def parameters(request):
    # delete empty jobs that longer then 2 hours
    for j in HgSpeciJob.objects.filter(CurrentStep=0):
        deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
        if deltaT > 3600 * 2:
            j.delete()

    # generate JobID
    try:
        lastjobid = HgSpeciJob.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1

    # occupy this JobID for 2 hours
    SPJob = HgSpeciJob(JobID=JobID)
    SPJob.save()

    return redirect('/hgspeci/parameters/%d/' % JobID)

def parameters_input(request, JobID):
    # get job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPElements.objects.filter(SPJobID=JobID)) > 0:
        SPElementsInlineFormSet = inlineformset_factory(HgSpeciJob, SPElements, form=SPElementsForm, extra=0,
                                                        can_delete=False)
    else:
        SPElementsInlineFormSet = inlineformset_factory(HgSpeciJob, SPElements, form=SPElementsForm, extra=1,
                                                        can_delete=False)

    if request.method == 'POST':
        paraform = ParameterForm(request.POST, request.FILES, instance=SPJob, prefix='main')
        formset = SPElementsInlineFormSet(request.POST, request.FILES, instance=SPJob, prefix='spelements')

        if paraform.is_valid() and formset.is_valid():
            model_instance = paraform.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1"
            model_instance.Successful = True
            model_instance.save()
            paraform.save()

            for form in formset.forms:
                form_instance = form.save(commit=False)
                form_instance.JobID = JobID
                #form_instance.save() # will be saved after submitted
            formset.save()

            return redirect('/hgspeci/review/%d' % int(JobID))
    else:
        paraform = ParameterForm(instance=SPJob, prefix='main')
        formset = SPElementsInlineFormSet(instance=SPJob, prefix='spelements')

    return render(request, 'hgspeci/parameters_input.html',
                  {'paraform': paraform, 'formset': formset, 'JobID': JobID})

def input_masterspecies(request, JobID):
    # get the job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPMasterSpecies.objects.filter(SPJobID=JobID)) > 0:
        SPMasterSpeciesInlineFormSet = inlineformset_factory(HgSpeciJob, SPMasterSpecies, form=SPMasterSpeciesForm,
                                                             extra=0, can_delete=False)
    else:
        SPMasterSpeciesInlineFormSet = inlineformset_factory(HgSpeciJob, SPMasterSpecies, form=SPMasterSpeciesForm,
                                                             extra=1, can_delete=False)
    # flag that indicate the parameters are submitted
    success = False

    if request.method == 'POST':
        paraform = ParameterForm(request.POST, request.FILES, instance=SPJob, prefix='main')
        masterformset = SPMasterSpeciesInlineFormSet(request.POST, request.FILES, instance=SPJob, prefix='spmaster')

        if paraform.is_valid() and masterformset.is_valid():
            model_instance = paraform.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1.1"
            model_instance.Successful = True
            model_instance.save()
            paraform.save()

            for form in masterformset.forms:
                form_instance = form.save(commit=False)
                form_instance.JobID = JobID
                #form_instance.save() # will be saved after submitted
            masterformset.save()

            #return redirect('/hgspeci/parameters/input_done/')
            success = True
    else:
        paraform = ParameterForm(instance=SPJob, prefix='main')
        masterformset = SPMasterSpeciesInlineFormSet(instance=SPJob, prefix='spmaster')

    return render(request, 'hgspeci/input_masterspecies.html',
                  {'paraform': paraform, 'masterformset': masterformset, 'success': success})

def input_solutionspecies(request, JobID):
    # get the job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPSolutionSpecies.objects.filter(SPJobID=JobID)) > 0:
        SPSolutionSpeciesInlineFormSet = inlineformset_factory(HgSpeciJob, SPSolutionSpecies, form=SPSolutionSpeciesForm,
                                                             extra=0, can_delete=False)
    else:
        SPSolutionSpeciesInlineFormSet = inlineformset_factory(HgSpeciJob, SPSolutionSpecies, form=SPSolutionSpeciesForm,
                                                             extra=1, can_delete=False)
    # flag that indicate the parameters are submitted
    success = False

    if request.method == 'POST':
        paraform = ParameterForm(request.POST, request.FILES, instance=SPJob, prefix='main')
        speciesformset = SPSolutionSpeciesInlineFormSet(request.POST, request.FILES, instance=SPJob, prefix='spspecies')

        if paraform.is_valid() and speciesformset.is_valid():
            model_instance = paraform.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1.2"
            model_instance.Successful = True
            model_instance.save()
            paraform.save()

            for form in speciesformset.forms:
                form_instance = form.save(commit=False)
                form_instance.JobID = JobID
                #form_instance.save() # will be saved after submitted
            speciesformset.save()

            #return redirect('/hgspeci/parameters/input_done/')
            success = True
    else:
        paraform = ParameterForm(instance=SPJob, prefix='main')
        speciesformset = SPSolutionSpeciesInlineFormSet(instance=SPJob, prefix='spspecies')

    return render(request, 'hgspeci/input_solutionspecies.html',
                  {'paraform': paraform, 'speciesformset': speciesformset, 'success': success})



def review(request, JobID):
    item = get_object_or_404(HgSpeciJob, JobID=JobID)
    return render(request, 'hgspeci/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    return render(request, 'hgspeci/review_doc.html')


def results(request, JobID, JobType='hgspeci'):
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    if item.CurrentStatus == '0':
        # the job is 'to be start', submit the job and jump to '1'

        # a function to start the job
        #### call some function here ####
        # a. generate input file
        # b. submit the job

        # prepare the necessary file for phreeqc
        jobmanger = JobManagement()
        jobmanger.HgspeciJobPrepare(obj=item, JobType=JobType)

        # run the calculations in background
        Exec_thread = threading.Thread(target=jobmanger.JobExec, kwargs={"obj": item, 'JobType': JobType})
        Exec_thread.start()


        # change the status in the database
        item.CurrentStatus = '1'
        item.Successful = True
        item.FailedReason = ''
        item.save()
        # redirect to the result page
        return redirect('/hgspeci/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
        # the job is 'running', keep checking the status
        return render(request, 'hgspeci/results_jobrunning.html', {'JobID': JobID, 'Item': item})
    if item.CurrentStatus == '2':
        # the job is finished, display the results.

        # collect results
        jobmanger = JobManagement()
        jobmanger.HgspeciCollectResults(obj=item, JobType=JobType)

        # get data for plotting the results
        job_dir = get_job_dir(JobID)

        csv = '%s/phreeqc-molality.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            pass

        # get species and pH values
        species = [str(i) for i in df.Species.values]
        pHs = [float(i) for i in df.columns.values[1:]]
        # generate a random color code
        colors = ['#'+''.join(np.random.permutation([i for i in '0123456789ABCDEF'])[:6]) for i in range(len(df))]

        # for molality
        data_molality = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_molality.append(di)

        # for activity
        csv = '%s/phreeqc-activity.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            pass
        data_activity = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_activity.append(di)

        # for logmolality
        csv = '%s/phreeqc-logmolality.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            pass
        data_logmolality = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_logmolality.append(di)

        # for logactivity
        csv = '%s/phreeqc-logactivity.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            pass
        data_logactivity = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_logactivity.append(di)

        # for gamma
        csv = '%s/phreeqc-gamma.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            pass
        data_gamma = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_gamma.append(di)

        return render(request, 'hgspeci/results.html',
                      {'JobID': JobID, 'Item': item, 'species': species, 'pHs': pHs,
                       'data_molality': data_molality,
                       'data_activity': data_activity,
                       'data_logmolality': data_logmolality,
                       'data_logactivity': data_logactivity,
                       'data_gamma': data_gamma,
                       })

    if item.CurrentStatus == '3':
        # there is some error in the job, display the error message.
        return render(request, 'hgspeci/results_error.html', {'JobID': JobID, 'Item': item})

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
                return render(request, 'hgspeci/results_doc.html', {'form': form})

            # show the result, if the JobID is available in the system
            return redirect('/hgspeci/results/%d' % int(model_instance.JobID))

    else:
        # the initial form
        form = QueryForm(initial={"JobID": ""})


    return render(request, 'hgspeci/results_doc.html', {'form': form})

def download(request, JobID, JobType='hgspeci'):
    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    if item.CurrentStatus == '2':
        # the job is finished, display the results.
        job_dir = get_job_dir(JobID)
        output_zip = '%s/%s-%s.zip' % (job_dir, JobType, JobID)
        if os.path.exists(output_zip):
            with open(output_zip, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/x-zip-compressed")
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(output_zip)
                return response

    raise Http404


# function for ajax query
def query_solutionmaster(request, ele):
    response_dict = {'success': True}
    response_dict['ele'] = ele
    try:
        master = SolutionMasterSpecies.objects.get(Element=ele)
    except:
        master = ''

    response_dict['master'] = master
    return render(request, 'hgspeci/solutionmaster.html', response_dict)

def query_solutionspecies(request, ele):
    response_dict = {'success': True}
    response_dict['ele'] = ele
    try:
        master = SolutionMasterSpecies.objects.get(Element=ele)
    except:
        master = ''

    if master:
        objs = SolutionSpecies.objects.filter(Reaction__contains=master.Species)
    else:
        objs = []

    response_dict['master'] = master
    response_dict['objs'] = objs
    return render(request, 'hgspeci/solutionspecies.html', response_dict)

# public functions
def get_job_dir(JobID, JobType='hgspeci'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir
