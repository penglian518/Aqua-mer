from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
#from .models import Compound, PKA, StabilityConstants, dGsolv, Refs
import os, json
import pandas as pd

from pHcalc.pHcalc import Acid
import numpy as np
from graphos.sources.simple import SimpleDataSource
#from graphos.renderers.yui import SplineChart
from graphos.renderers.matplotlib_renderer import LineChart

import django
import matplotlib
matplotlib.use('Agg')
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
try:
    # python 2
    from StringIO import StringIO
except ImportError:
     # python 3
     from io import BytesIO as StringIO
import base64


# Create your views here.
PWD = os.path.abspath(os.curdir)
PRJ_DIR = 'calculations/projects/mercury_complex'


def index(request):

    #prjs = os.listdir('calculations/projects')
    cals = sorted([i for i in os.listdir('%s/output/' % PRJ_DIR) if os.path.isdir('%s/output/%s' % (PRJ_DIR, i))])
    #return HttpResponse(cwd)

    # list all the reaction groups to display on index page
    reaction_groups_to_display = ['Gsolv_bench',
    'logK_Thapa_w0', 'logK_Namazian_w0', 'logK_amines_w0',
    'logK_CH3CHSHCOOH_w0', 'logK_CH3COO', 'logK_CH3NH2_w0',
    'logK_Cl_w0', 'logK_Cl_w2WAT2', 'logK_H2O_w0', 'logK_H2O_w2WAT2',
    'logK_NH3_w0', 'logK_NH3_w2WAT2']


    AllPerformance = []
    for level in cals:

        reaction_groups = search_results_for_onelevel(level)

        method_performance = {
            'level': level,
        }

        for reaction in reaction_groups_to_display:
            # get performace dict for the reaction group
            try:
                performance = [i for i in reaction_groups if i['Name'] == reaction][0]
            except IndexError:
                performance = {}

            # format performace data
            if len(performance) > 0:
                performance_for_display = '%s(%s):%s' % (str(performance['MUE']), str(performance['SD']), str(performance['nReactions']))
            else:
                performance_for_display = '-'

            # add to method_performance dict
            method_performance[reaction] = performance_for_display

        AllPerformance.append(method_performance)

    return render(request,
                  'calculations/index.html',
                  {
                      #'CurrentCalculations': cals,
                      'CurrentCalculations': AllPerformance,
                      'ReactionGroups': reaction_groups_to_display
                   },
                  )



def search_results_for_onelevel(level):
    csv_folder = '%s/output/%s/csv' % (PRJ_DIR, level)
    csv_files = sorted([i for i in os.listdir(csv_folder) if i[-4:] in ['.csv', '.CSV']])

    reaction_groups = []
    for csv in csv_files:
        df = pd.DataFrame.from_csv('%s/%s' % (csv_folder, csv))
        
        # recal difference for Gsolv data
        try:
            if list(set(list(df.Constant.values)))[0] in ['Gsolv']:
                df.Difference = (df.deltaG - df.Experimental)
        except:
            pass

        if len(df) == 0:
            MSE = 0
            MUE = 0
            SD = 0
        else:
            MSE = df.Difference.mean()
            #MUE = sum((df.Difference - MSE) ** 2) ** 0.5
            MUE = df.Difference.abs().mean()
            SD = df.Difference.std()

        reaction_para = {'Name': csv[:-4],
                           'nReactions': len(df),
                           'MSE': round(MSE, 2),
                           'MUE': round(MUE, 2),
                           'SD': round(SD, 2)}
        reaction_groups.append(reaction_para)
    return reaction_groups



def onelevel(request, level):
    reaction_groups = search_results_for_onelevel(level)

    return render(request,
                  'calculations/onelevel.html',
                  {
                      'QMLevel': level,
                      'ReactionGroups': reaction_groups,
                  },
                  )

def plotlogk(request, logk_pair):
    logk_cal = float(logk_pair.split('_')[0])
    logk_exp = float(logk_pair.split('_')[1])

    # for logk_cal
    phs = np.linspace(0, 25, 100)
    p = Acid(pKa=[logk_cal], charge=0, conc=0.01)
    fracs = p.alpha(phs)
    '''
    data_cal = [['pH', 'L-', 'ML']]
    for i in range(len(phs)):
        data_cal += [[phs[i]] + list(fracs[i])]
    chartCal = LineChart(SimpleDataSource(data=data_cal), options={'title': 'logK (Prediction)'})
    '''

    # for logk_exp
    pexp = Acid(pKa=[logk_exp], charge=0, conc=0.01)
    fracs_exp = pexp.alpha(phs)
    #data_exp = [['pH', 'L-(cal)', 'ML(cal)', 'L-(exp)', 'ML(exp)']]
    #for i in range(len(phs)):
    #    data_exp += [[phs[i]] + list(fracs[i]) + list(fracs_exp[i])]
    #chartExp = LineChart(SimpleDataSource(data=data_exp), options={'title': 'logK (Experiment)'})


    # plot the figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(phs, fracs[:, 0], 'r-', label='L- (Cal %.2f)' % logk_cal, linewidth=3)
    ax.plot(phs, fracs[:, 1], 'b-', label='ML (Cal %.2f)' % logk_cal, linewidth=3)
    ax.plot(phs, fracs_exp[:, 0], 'm--', label='L- (Exp %.2f)' % logk_exp, linewidth=3)
    ax.plot(phs, fracs_exp[:, 1], 'c-.', label='ML (Exp %.2f)' % logk_exp, linewidth=3)
    #ax.text(logk_cal+0.3, 0.5, str(round(logk_cal, 2)), fontsize=14)
    #ax.text(logk_exp+0.3, 0.5, str(round(logk_exp, 2)), fontsize=14)
    ax.legend(frameon=False)
    ax.set_xlabel('pH', fontsize=14)
    ax.set_ylabel('Percentage (%)', fontsize=14)

    # format convert for output
    out = StringIO()
    plt.savefig(out)
    out.seek(0)
    fig_in_base64 = "data:image/png;base64,%s" % base64.encodestring(out.read())

    return render(request, "calculations/plotlogk_v1.html", {'chart': fig_in_base64})


    '''
    # this version is for graphos
    return render(request,
                  'calculations/plotlogk.html',
                  {
                   #'chartCal': chartCal,
                   'chartExp': chartExp,
                   'logkCal': logk_cal,
                   'logkExp': logk_exp,
                  })
    '''

def onereactiongroup(request, level, reaction_group):
    csv = '%s/output/%s/csv/%s.csv' % (PRJ_DIR, level, reaction_group)
    linear_fig = '%s/output/%s/fig/linear_dG_explogK_%s.png' % (PRJ_DIR, level, reaction_group)
    #linear_fig1 = '%s/output/%s/fig/linear_charge_explogK_%s.png' % (PRJ_DIR, level, reaction_group)
    linear_fig1 = '%s/output/%s/fig/linear_callogK_explogK_%s.png' % (PRJ_DIR, level, reaction_group)

    if os.path.exists(linear_fig):
        LinearFig = True
    else:
        LinearFig = False

    if os.path.exists(linear_fig1):
        LinearFig1 = True
    else:
        LinearFig1 = False

    print '\n%s\n' % linear_fig
    print '\n%s\n' % linear_fig1

    df = pd.DataFrame.from_csv(csv)

    # recal difference for Gsolv data
    try:
        if list(set(list(df.Constant.values)))[0] in ['Gsolv']:
            df.Difference = (df.deltaG - df.Experimental)
    except:
        pass

    MSE = df.Difference.mean()
    #MUE = sum((df.Difference - MSE)**2)**0.5
    MUE = df.Difference.abs().mean()
    SD = df.Difference.std()

    Errors = {
        'MSE': round(MSE, 2),
        'MUE': round(MUE, 2),
        'SD': round(SD, 2),
        'Name': reaction_group,
    }

    Data = []
    counter = 0
    while counter < len(df):
        dfi = df.ix[counter]
        dfi['ReactantsBSafeNames'] = json.loads(dfi['ReactantsBSafe']).keys()
        dfi['ProductsBSafeNames'] = json.loads(dfi['ProductsBSafe']).keys()
        try:
            dfi['CalsubExp'] = dfi['deltaG'] - dfi['Experimental']
        except:
            pass

        Data.append(dfi)
        counter += 1

    return render(request,
                  'calculations/onereactiongroup.html',
                  {
                      'ProjectName': os.path.basename(PRJ_DIR),
                      'PATHtoLevel': '%s/output/%s' % (os.path.basename(PRJ_DIR), level),
                      'ReactionsResults': Data,
                      'Errors': Errors,
                      'LinearFig': LinearFig,
                      'LinearFig1': LinearFig1,
                  },
                  )
