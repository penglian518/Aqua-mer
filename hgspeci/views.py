from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms import inlineformset_factory
from .models import HgSpeciJob, SPElements, SPElementsForm, ParameterForm, SPDBtoUseForm
from .models import SPMasterSpecies, SPMasterSpeciesForm, SPSolutionSpecies, SPSolutionSpeciesForm, QueryForm
from phreeqcdb.models import SolutionMasterSpecies, SolutionSpecies
from calcdata.models import CalcSolutionMasterSpecies, CalcSolutionSpecies
from cyshg.models import AllJobIDs
from pka.models import pKaJob
from gsolv.models import GSolvJob
from logk.models import LogKJob

from scripts.JobManagement import JobManagement
from scripts.PhreeqcPrepare import PhreeqcPrepare
from scripts.VistorStatistics import clientStatistics
import threading
import base64, os, datetime, json
import pandas as pd
import numpy as np
from decimal import Decimal

from colour import Color

# Create your views here.


def index(request):
    clientStatistics(request)
    return render(request, 'hgspeci/index.html')


def parameters(request):
    clientStatistics(request)
    # delete empty jobs that longer then 2 hours
    for j in HgSpeciJob.objects.filter(CurrentStep=0):
        deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
        if deltaT > 3600 * 2:
            j.delete()
    '''
    # generate JobID
    try:
        lastjobid = HgSpeciJob.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1
    '''
    JobID = generate_JobID()
    # occupy this JobID for 2 hours
    SPJob = HgSpeciJob(JobID=JobID)
    SPJob.save()

    return redirect('/hgspeci/parameters/%d/' % JobID)

def parameters_input(request, JobID):
    clientStatistics(request)
    # get job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPElements.objects.filter(JobID=JobID)) > 0:
        SPElementsInlineFormSet = inlineformset_factory(HgSpeciJob, SPElements, form=SPElementsForm, extra=0,
                                                        can_delete=False)
    else:
        SPElementsInlineFormSet = inlineformset_factory(HgSpeciJob, SPElements, form=SPElementsForm, extra=1,
                                                        can_delete=False)

    if request.method == 'POST':
        paraform = ParameterForm(request.POST, request.FILES, instance=SPJob, prefix='main')
        formset = SPElementsInlineFormSet(request.POST, request.FILES, instance=SPJob, prefix='spelements')
        dbform = SPDBtoUseForm(request.POST, request.FILES, instance=SPJob, prefix='db')

        if dbform.is_valid():
            model_instance = dbform.save(commit=False)
            model_instance.JobID = JobID
            model_instance.CurrentStep = "1.1"
            model_instance.Successful = True
            model_instance.save()
            dbform.save()

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
        dbform = SPDBtoUseForm(instance=SPJob, prefix='db')

    return render(request, 'hgspeci/parameters_input.html',
                  {'paraform': paraform, 'formset': formset, 'dbform': dbform, 'JobID': JobID})

def input_masterspecies(request, JobID):
    #clientStatistics(request)
    # get the job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPMasterSpecies.objects.filter(JobID=JobID)) > 0:
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
    #clientStatistics(request)
    # get the job handle
    try:
        SPJob = HgSpeciJob.objects.get(JobID=JobID)
    except:
        SPJob = HgSpeciJob(JobID=JobID)

    # determine how many input areas should provide
    if len(SPSolutionSpecies.objects.filter(JobID=JobID)) > 0:
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


def elements(request):
    '''This function displays all avaialbe elemetns in the database'''
    #clientStatistics(request)
    # from phreeqcdb
    all_master = SolutionMasterSpecies.objects.all()
    all_master = sorted(all_master, key=lambda x: x.Element)
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    # from calcdata
    all_master_calc = CalcSolutionMasterSpecies.objects.all()
    all_master_calc = sorted(all_master_calc, key=lambda x: x.Element)
    # get refs
    all_refs_calc = []
    for p in all_master_calc:
        all_refs_calc.append(p.Ref)

    return render(request, 'hgspeci/elements.html',
                  {'all_master': all_master, 'refs': list(set(all_refs)),
                   'all_master_calc': all_master_calc, 'refs_calc': list(set(all_refs_calc))}
                  )



def review(request, JobID):
    clientStatistics(request)
    item = get_object_or_404(HgSpeciJob, JobID=JobID)
    return render(request, 'hgspeci/review.html', {'JobID': JobID, 'Item': item})

def review_doc(request):
    clientStatistics(request)
    return render(request, 'hgspeci/review_doc.html')


def results(request, JobID, JobType='hgspeci'):
    # if the job hasn't been started, start the job.
    # if the job is running, check every 5 seconds.
    # if the job has finished, display the results.
    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    if item.CurrentStatus == '0':
        clientStatistics(request)
        # the job is 'to be start', submit the job and jump to '1'

        # change the status in the database
        item.CurrentStatus = '1'
        item.Successful = True
        item.FailedReason = ''
        item.save()
        # redirect to the result page
        return redirect('/hgspeci/results/%d' % int(item.JobID))

    if item.CurrentStatus == '1':
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

        # the job is 'running', keep checking the status
        return render(request, 'hgspeci/results_jobrunning.html', {'JobID': JobID, 'Item': item})
    if item.CurrentStatus == '2':
        clientStatistics(request)
        # the job is finished, display the results.


        # get data for plotting the results
        job_dir = get_job_dir(JobID)

        csv = '%s/speciation-molality.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
            df = df[df.Species != 'H2O']
            df.index = range(len(df))
        except:
            item.Successful = False
            item.FailedReason = 'Could not find file %s' % os.path.basename(csv)
            return render(request, 'hgspeci/results_error.html', {'JobID': JobID, 'Item': item})

        # get species and pH values
        species = [str(i) for i in df.Species.values]
        pHs = [float(i) for i in df.columns.values[1:]]

        chartType = 'line'
        if len(pHs) == 1:
            chartType = 'bar'

        # generate color does
        red = Color("red")
        blue = Color("blue")
        try:
            # generate color gradient
            colors = [blue.get_hex_l(), red.get_hex_l()] + [i.get_hex_l() for i in list(blue.range_to(red, len(species)-2))]
            #colors = [i.get_hex_l() for i in list(blue.range_to(red, len(species)))]

            ## sort the color according to charges
            charges = [getCharge(m) for m in species]
            sp_ch = sorted(zip(species, charges), key=lambda x: x[1])
            sp_color = dict(zip([i[0] for i in sp_ch], colors))
            colors = [sp_color[i] for i in species]
        except:
            # generate a random color code
            colors = ['#'+''.join(np.random.permutation([i for i in '0123456789ABCDEF'])[:6]) for i in range(len(df))]
        # generate a random color code
        colors = ['#'+''.join(np.random.permutation([i for i in '0123456789ABCDEF'])[:6]) for i in range(len(df))]

        # for molality
        data_molality = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_molality.append(di)

        # for activity
        csv = '%s/speciation-activity.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
            df = df[df.Species != 'H2O']
            df.index = range(len(df))
        except:
            pass
        data_activity = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_activity.append(di)

        # for logmolality
        csv = '%s/speciation-logmolality.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
            df = df[df.Species != 'H2O']
            df.index = range(len(df))
        except:
            pass
        data_logmolality = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_logmolality.append(di)

        # for logactivity
        csv = '%s/speciation-logactivity.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
            df = df[df.Species != 'H2O']
            df.index = range(len(df))
        except:
            pass
        data_logactivity = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_logactivity.append(di)

        # for gamma
        csv = '%s/speciation-gamma.csv' % job_dir
        try:
            df = pd.DataFrame.from_csv(csv)
            df = df[df.Species != 'H2O']
            df.index = range(len(df))
        except:
            pass
        data_gamma = []
        for idx in range(len(df)):
            di = {'name': df.ix[idx].values[0], 'data':['%.2E' % Decimal(float(i)) for i in df.ix[idx].values[1:]]}
            di['color'] = colors[idx]
            data_gamma.append(di)

        return render(request, 'hgspeci/results.html',
                      {'JobID': JobID, 'Item': item, 'species': species, 'pHs': pHs, 'chartType': chartType,
                       'data_molality': data_molality,
                       'data_activity': data_activity,
                       'data_logmolality': data_logmolality,
                       'data_logactivity': data_logactivity,
                       'data_gamma': data_gamma,
                       })

    if item.CurrentStatus == '3':
        clientStatistics(request)
        # there is some error in the job, display the error message.
        return render(request, 'hgspeci/results_error.html', {'JobID': JobID, 'Item': item})

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
                return render(request, 'hgspeci/results_doc.html', {'form': form})

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


    return render(request, 'hgspeci/results_doc.html', {'form': form})

def download(request, JobID, JobType='hgspeci'):
    #clientStatistics(request)
    item = get_object_or_404(HgSpeciJob, JobID=JobID)

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


# function for ajax query
def query_solutionmaster(request, JobID, ele):
    #clientStatistics(request)
    response_dict = {'success': True}
    response_dict['ele'] = ele

    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    # genearte the query string.
    phreeqc = PhreeqcPrepare()
    query_str, query_str_calc = phreeqc.genQueryStr(item, type='SolutionMasterSpecies', string=ele, string_calc=ele)

    masters = []
    master_calc = []
    try:
        master = list(SolutionMasterSpecies.objects.filter(eval(query_str)))
    except:
        master = []

    try:
        master_calc = list(CalcSolutionMasterSpecies.objects.filter(eval(query_str_calc)))
    except:
        master_calc = []

    # remove repeat species
    master_species = [i.Species for i in master]
    master_calc_new = []
    for j in master_calc:
        if j.Species not in master_species:
            master_calc_new.append(j)

    if master:
        masters += master
    if master_calc:
        masters += master_calc_new

    response_dict['masters'] = masters
    return render(request, 'hgspeci/solutionmaster.html', response_dict)

def query_solutionspecies(request, JobID, ele):
    #clientStatistics(request)
    response_dict = {'success': True}
    response_dict['ele'] = ele

    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    try:
        master = SolutionMasterSpecies.objects.get(Element=ele)
        master_species = master.Species
    except:
        master = ''
        master_species = False
    try:
        master_calc = CalcSolutionMasterSpecies.objects.get(Element=ele)
        master_calc_species = master_calc.Species
    except:
        master_calc = ''
        master_calc_species = False

    # genearte the query string.
    phreeqc = PhreeqcPrepare()
    query_str, query_str_calc = phreeqc.genQueryStr(item, type='SolutionSpecies', string=master_species, string_calc=master_calc_species)

    objs = []
    if master:
        objs = list(SolutionSpecies.objects.filter(eval(query_str)))

    objs_calc = []
    if master_calc:
        objs_calc = list(CalcSolutionSpecies.objects.filter(eval(query_str_calc)))


    # remove repeat obj
    reactions = [i.Reaction for i in objs]
    objs_calc_new = []
    for j in objs_calc:
        if j.Reaction not in reactions:
            objs_calc_new.append(j)

    response_dict['master'] = master
    response_dict['objs'] = objs + objs_calc_new
    response_dict['master_calc'] = master_calc
    response_dict['objs_calc'] = objs_calc_new
    return render(request, 'hgspeci/solutionspecies.html', response_dict)

def query_elements(request, JobID):
    #clientStatistics(request)
    item = get_object_or_404(HgSpeciJob, JobID=JobID)

    if request.is_ajax():
        ele = request.GET.get('term', '')

        # genearte the query string.
        phreeqc = PhreeqcPrepare()
        query_str, query_str_calc = phreeqc.genQueryStr(item, type='Element', string=ele, string_calc=ele)

        masters = []
        master_calc = []
        try:
            master = list(SolutionMasterSpecies.objects.filter(eval(query_str)))
        except:
            master = []

        try:
            master_calc = list(CalcSolutionMasterSpecies.objects.filter(eval(query_str_calc)))
        except:
            master_calc = []

        # remove repead species
        master_species = [i.Species for i in master]
        master_calc_new = []
        for j in master_calc:
            if j.Species not in master_species:
                master_calc_new.append(j)

        if master:
            masters += master
        if master_calc:
            masters += master_calc_new

        #response_data = [{'value': i.Element} for i in masters]
        response_data = [i.Element for i in masters]
        if len(response_data) > 10 :
            response_data = response_data[:10]

        json_data = json.dumps(response_data)
    else:
        json_data = 'fail'
    return HttpResponse(json_data, content_type="application/json")

def save_db_selection(request, JobID, SelectedDB):
    #clientStatistics(request)
    try:
        item = HgSpeciJob.objects.get(JobID=JobID)
        item.SPDBtoUse = SelectedDB
        item.save()
        return HttpResponse('Saved')
    except:
        return HttpResponse('Not saved')

# public functions
def get_job_dir(JobID, JobType='hgspeci'):
    DjangoHome = '/home/p6n/workplace/website/cyshg'
    JobLocation = 'media/%s/jobs' % JobType

    job_dir = '%s/%s/%s' % (DjangoHome, JobLocation, JobID)

    return job_dir

def generate_JobID(module=AllJobIDs):
    try:
        lastjobid = module.objects.last().id
    except AttributeError:
        lastjobid = 0
    JobID = lastjobid + 1

    # register that job
    newjob = module.objects.create()
    newjob.JobID = JobID
    newjob.JobType = 'hgspeci'
    newjob.save()

    return JobID


def getCharge(mol):
    charge = 0
    if mol.find('+') > 0:
        idx = mol.find('+')
        if idx + 1 == len(mol):
            charge = 1
        else:
            charge = int(mol[idx:])
    elif mol.find('-') > 0:
        idx = mol.find('-')
        if idx + 1 == len(mol):
            charge = -1
        else:
            charge = int(mol[idx:])
    return charge
