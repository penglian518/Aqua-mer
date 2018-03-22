from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import CalcSolutionMasterSpecies, CalcSolutionSpecies
from scripts.VistorStatistics import clientStatistics
# Create your views here.
def index(request):
    clientStatistics(request)
    NumElements = CalcSolutionMasterSpecies.objects.count()
    NumSpecies = CalcSolutionSpecies.objects.count()

    return render(request, 'calcdata/index.html',
                  {'NumElements': NumElements,
                  'NumSpecies': NumSpecies,
                   })



def master(request):
    clientStatistics(request)
    all_master = CalcSolutionMasterSpecies.objects.all()
    all_master = sorted(all_master, key=lambda x: x.Element)
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    return render(request, 'calcdata/master.html',
                  {'all_master': all_master, 'refs': list(set(all_refs))})

def species(request):
    clientStatistics(request)
    all_species = CalcSolutionSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)

    return render(request, 'calcdata/species.html',
                  {'all_species': all_species, 'refs': list(set(all_refs))})

def xyz(request, ID):
    clientStatistics(request)
    DjangoHome = '/home/p6n/workplace/website/cyshg'

    item = get_object_or_404(CalcSolutionMasterSpecies, id=ID)

    # get refs
    xyzfile = '%s/%s' % (DjangoHome, item.XYZ)

    fcon = ''.join(open(xyzfile).readlines())

    return HttpResponse(fcon, content_type='text/plain')

def viewxyz(request, ID):
    clientStatistics(request)
    item = get_object_or_404(CalcSolutionMasterSpecies, id=ID)

    return render(request, 'calcdata/viewxyz.html',
                  {'Item': item})
