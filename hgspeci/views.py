from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory
from .models import HgSpeciJob, SPElements, SPElementsForm, ParameterForm
from .models import SPMasterSpecies, SPMasterSpeciesForm, SPSolutionSpecies, SPSolutionSpeciesForm
from phreeqcdb.models import SolutionMasterSpecies, SolutionSpecies

from scripts.JobManagement import JobManagement
import threading
import base64, os, datetime

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

    jobmanger = JobManagement()
    jobmanger.HgspeciJobPrepare(obj=item)

    return render(request, 'hgspeci/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    return render(request, 'hgspeci/review_doc.html')



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

