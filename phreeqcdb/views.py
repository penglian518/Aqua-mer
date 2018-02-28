from django.shortcuts import render

from .models import SolutionMasterSpecies, SolutionSpecies, Phases, SurfaceMasterSpecies, SurfaceSpecies,\
                    ExchangeMasterSpecies, ExchangeSpecies, Rates, Refs

# Create your views here.
def index(request):
    NumElements = SolutionMasterSpecies.objects.count()
    NumSpecies = SolutionSpecies.objects.count()
    NumPhases = Phases.objects.count()
    NumSurfaceMasters = SurfaceMasterSpecies.objects.count()
    NumSurfaceSpecies = SurfaceSpecies.objects.count()
    NumExchangeMasters = ExchangeMasterSpecies.objects.count()
    NumExchangeSpecies = ExchangeSpecies.objects.count()
    NumRates = Rates.objects.count()

    return render(request, 'phreeqcdb/index.html',
                  {'NumElements': NumElements,
                  'NumSpecies': NumSpecies,
                  'NumPhases': NumPhases,
                   'NumSurfaceMasters': NumSurfaceMasters,
                   'NumSurfaceSpecies': NumSurfaceSpecies,
                   'NumExchangeMasters': NumExchangeMasters,
                   'NumExchangeSpecies': NumExchangeSpecies,
                   'NumRates': NumRates,
                   })



def master(request):
    all_master = SolutionMasterSpecies.objects.all()
    all_master = sorted(all_master, key=lambda x: x.Element)
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/master.html',
                  {'all_master': all_master, 'refs': list(set(all_refs))})

def species(request):
    all_species = SolutionSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/species.html',
                  {'all_species': all_species, 'refs': list(set(all_refs))})

def phases(request):
    all_phases = Phases.objects.all()
    # get refs
    all_refs = []
    for p in all_phases:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/phases.html',
                  {'all_phases': all_phases, 'refs': list(set(all_refs))})

def surfacemaster(request):
    all_master = SurfaceMasterSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/surfacemaster.html',
                  {'all_master': all_master, 'refs': list(set(all_refs))})

def surfacespecies(request):
    all_species = SurfaceSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/surfacespecies.html',
                  {'all_species': all_species, 'refs': list(set(all_refs))})

def exchangemaster(request):
    all_master = ExchangeMasterSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/exchangemaster.html',
                  {'all_master': all_master, 'refs': list(set(all_refs))})

def exchangespecies(request):
    all_species = ExchangeSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/exchangespecies.html',
                  {'all_species': all_species, 'refs': list(set(all_refs))})

def rates(request):
    all_rates = Rates.objects.all()
    # get refs
    all_refs = []
    for p in all_rates:
        all_refs.append(p.Ref)

    return render(request, 'phreeqcdb/rates.html',
                  {'all_rates': all_rates, 'refs': list(set(all_refs))})
