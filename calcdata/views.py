from django.shortcuts import render

from .models import CalcSolutionMasterSpecies, CalcSolutionSpecies

# Create your views here.
def index(request):
    NumElements = CalcSolutionMasterSpecies.objects.count()
    NumSpecies = CalcSolutionSpecies.objects.count()

    return render(request, 'calcdata/index.html',
                  {'NumElements': NumElements,
                  'NumSpecies': NumSpecies,
                   })



def master(request):
    all_master = CalcSolutionMasterSpecies.objects.all()
    all_master = sorted(all_master, key=lambda x: x.Element)
    # get refs
    all_refs = []
    for p in all_master:
        all_refs.append(p.Ref)

    return render(request, 'calcdata/master.html',
                  {'all_master': all_master, 'refs': list(set(all_refs))})

def species(request):
    all_species = CalcSolutionSpecies.objects.all()
    # get refs
    all_refs = []
    for p in all_species:
        all_refs.append(p.Ref)

    return render(request, 'calcdata/species.html',
                  {'all_species': all_species, 'refs': list(set(all_refs))})
