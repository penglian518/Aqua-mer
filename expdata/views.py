from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Compound, PKA, StabilityConstants, dGsolv, Refs

from scripts.VistorStatistics import clientStatistics
# Create your views here.

def index(request):
    clientStatistics(request)
    all_compounds = Compound.objects.all()
    all_pkas = PKA.objects.all()
    all_stabilities = StabilityConstants.objects.all()
    all_dgsov = dGsolv.objects.all()
    return render(request,
                  'expdata/index.html',
                  {'NumBasicInfo': len(all_compounds),
                   'Numpka': len(all_pkas),
                   'Numstabilities': len(all_stabilities),
                   'Numdgsolv': len(all_dgsov),
                   },
                  )


def basic(request):
    clientStatistics(request)
    all_compounds = Compound.objects.all()
    return render(request,
                  'expdata/basic.html',
                  {'cpds': all_compounds,
                   },
                  )

def dgsolv(request):
    clientStatistics(request)
    all_dgsov = dGsolv.objects.all()
    #all_refs = Refs.objects.all()
    # get refs
    all_refs = []
    for p in all_dgsov:
        all_refs.append(p.dGsolvReference)

    all_refs = set(all_refs)

    return render(request,
                  'expdata/dgsolv.html',
                  {
                   'dgsolvs': all_dgsov,
                   'refs': all_refs,
                  },
                  )

def pka(request):
    clientStatistics(request)
    all_pkas = PKA.objects.all()

    # get refs
    all_refs = []
    for p in all_pkas:
        all_refs.append(p.pKaReference)
        all_refs.append(p.ThermalReference)

    all_refs = set(all_refs)
    return render(request,
                  'expdata/pka.html',
                  {
                   'pkas': all_pkas,
                   'refs': all_refs,
                  },
                  )


def stability(request):
    clientStatistics(request)
    all_stabilities = StabilityConstants.objects.all()
    #all_refs = Refs.objects.all()
    # get refs
    all_refs = []
    for p in all_stabilities:
        all_refs.append(p.ThermalReference)

    all_refs = set(all_refs)

    return render(request,
                  'expdata/stability.html',
                  {
                   'stabilities': all_stabilities,
                   'refs': all_refs,
                  },
                  )


def onecpd(request, args, value):
    clientStatistics(request)
    # get the compound
    if args in ['id', 'pk']:
        try:
            cpds = Compound.objects.filter(id=value)
        except:
            return HttpResponse('Compound does not exist.')
    elif args in ['pubchem', 'pub', 'pubid', 'pubchemid', 'PubChemID', 'PubChem']:
        try:
            cpds = Compound.objects.filter(PubChemID=value)
        except:
            return HttpResponse('Compound does not exist.')

    all_pkas = PKA.objects.filter(MolID=cpds)
    all_stabilities = StabilityConstants.objects.filter(MolID=cpds)
    all_dgsov = dGsolv.objects.filter(MolID=cpds)

    # get refs
    all_refs = []
    for p in all_dgsov:
        all_refs.append(p.dGsolvReference)
    for p in all_pkas:
        all_refs.append(p.pKaReference)
        all_refs.append(p.ThermalReference)
    for p in all_stabilities:
        all_refs.append(p.ThermalReference)

    all_refs = set(all_refs)

    return render(request,
                  'expdata/onecpd.html',
                  {'cpds': cpds,
                   'pkas': all_pkas,
                   'stabilities': all_stabilities,
                   'dgsolvs': all_dgsov,
                   'refs': all_refs,
                   },
                  )
