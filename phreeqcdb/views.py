from django.shortcuts import render
from django.db.models import Q
from .models import SolutionMasterSpecies, SolutionSpecies, Phases, SurfaceMasterSpecies, SurfaceSpecies,\
                    ExchangeMasterSpecies, ExchangeSpecies, Rates, Refs

from scripts.VistorStatistics import clientStatistics
# Create your views here.
def index(request):
    clientStatistics(request)

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
    clientStatistics(request)
    all_master = SolutionMasterSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    all_master = sorted(all_master, key=lambda x: x.Element)
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_master:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/master.html',
                  {'all_master': all_master, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def species(request):
    clientStatistics(request)
    all_species = SolutionSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_species:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/species.html',
                  {'all_species': all_species, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def phases(request):
    clientStatistics(request)
    all_phases = Phases.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_phases:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_phases:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/phases.html',
                  {'all_phases': all_phases, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def surfacemaster(request):
    clientStatistics(request)
    all_master = SurfaceMasterSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_master:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/surfacemaster.html',
                  {'all_master': all_master, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def surfacespecies(request):
    clientStatistics(request)
    all_species = SurfaceSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_species:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/surfacespecies.html',
                  {'all_species': all_species, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def exchangemaster(request):
    clientStatistics(request)
    all_master = ExchangeMasterSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_master:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/exchangemaster.html',
                  {'all_master': all_master, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def exchangespecies(request):
    clientStatistics(request)
    all_species = ExchangeSpecies.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_species:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/exchangespecies.html',
                  {'all_species': all_species, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})

def rates(request):
    clientStatistics(request)
    all_rates = Rates.objects.filter(~Q(DBSource__DBID__contains='test'))
    # get refs
    all_refs = []
    for p in all_rates:
        all_refs.append(p.Ref)
    # get DBs
    all_DBs = []
    for p in all_rates:
        all_DBs.append(p.DBSource)

    return render(request, 'phreeqcdb/rates.html',
                  {'all_rates': all_rates, 'refs': list(set(all_refs)), 'dbs': list(set(all_DBs))})
