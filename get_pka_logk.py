#!/usr/bin/env python
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
django.setup()

import pandas as pd
from expdata.models import Compound, PKA, StabilityConstants, dGsolv, Refs



cpds = Compound.objects.all()

df = pd.DataFrame()

for p in cpds:
    pdS = pd.Series()

    pdS['id'] = p.id
    pdS['PubChemID'] = p.PubChemID
    pdS['Name'] = p.Name
    pdS['Formula'] = p.Formula

    # get all pKa values
    pKas = p.pka_set.get_queryset()
    species_set = sorted(set([i.Species for i in pKas]))
    if len(species_set) > 1:
        species = species_set[-2]
    elif len(species_set) == 1:
        species = species_set[-1]

    pKas_list = [(i, i.IonicStrength) for i in pKas if i.Species == species]
    pKas_sorted = sorted(pKas_list, key=lambda x: x[1])
    if len(pKas_sorted) > 0:
        pka = pKas_sorted[0][0]
        pdS['pKa_Species'] = pka.Species
        pdS['pKa_Ionic'] = pka.IonicStrength
        pdS['pKa'] = pka.pKa

    # get all logKs
    logKs = p.stabilityconstants_set.get_queryset()
    logKs_list = [(i, i.IonicStrength) for i in logKs if i.Species == 'ML']
    logKs_sorted = sorted(logKs_list, key=lambda x: x[1])
    if len(logKs_sorted) > 0:
        logk = logKs_sorted[0][0]
        pdS['logK_Species'] = logk.Species
        pdS['logK_Ionic'] = logk.IonicStrength
        pdS['logK'] = logk.LogBorK

    if len(pKas_sorted) > 0 and len(logKs_sorted) > 0:
        df = df.append([pdS])

df.index = range(len(df))
print df