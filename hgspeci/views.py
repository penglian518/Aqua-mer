from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory
from .models import HgSpeciJob, SPElements, SPElementsForm, ParameterForm
from phreeqcdb.models import SolutionMasterSpecies, SolutionSpecies

from scripts.JobManagement import JobManagement
import threading
import base64, os

# Create your views here.


def index(request):
    return render(request, 'hgspeci/index.html')

def parameters_input(request):
    # generate JobID
    try:
        lastjobid = HgSpeciJob.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1

    SPJob = HgSpeciJob()
    SPElementsInlineFormSet = inlineformset_factory(HgSpeciJob, SPElements, form=SPElementsForm, extra=1, can_delete=False)

    if request.method == 'POST':
        paraform = ParameterForm(request.POST, request.FILES, instance=SPJob, prefix='main')
        formset = SPElementsInlineFormSet(request.POST, request.FILES, instance=SPJob, prefix='nested')

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

            return redirect('/hgspeci/')
    else:
        paraform = ParameterForm(instance=SPJob, prefix='main')
        formset = SPElementsInlineFormSet(instance=SPJob, prefix='nested')

    return render(request, 'hgspeci/parameters_input.html', {'paraform': paraform, 'formset': formset})



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

