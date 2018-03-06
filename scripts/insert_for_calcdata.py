#!/usr/bin/env python
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
django.setup()

import logging, shutil
import pandas as pd
from calcdata.models import CalcSolutionMasterSpecies, CalcSolutionSpecies, Refs
import json

class insert_for_calcdata:
    def __init__(self):
        self.BaseDirforCalc = '/home/p6n/workplace/mercury_complex'
        self.BaseDir = '/data/p6n/workplace/website/cyshg'
        self.convertDict = {0:'o', 1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h', 9:'i'}

    def insert_solution_master_species(self, csv, Basename='Thiol', xyzDir='calcdata/data/Thiol/M062X_631+Gdp_SDD_SMD_SAS_Alpha0485/xyz'):
        '''
        This functional is just help to insert solution master species. One has to double check the results manually.
        '''
        try:
            df = pd.DataFrame.from_csv(csv)
        except:
            logging.warn('Failed to load the file %s' % csv)
            return 1

        # clean the data frame, to include only molecules suitable for master species
        #df_anions = df[df.Charge < 0].drop_duplicates()
        df_anions = df[df.Reactant == 1]
        df_anions_noH = df_anions[df_anions.Source.apply(lambda x: x.find('H') < 0)]
        df_cleaned = df_anions_noH.sort_values(by=['GFWforElement', 'IUPACName'])

        # insert
        for idx in df_cleaned.index.values:
            dfi = df_cleaned.ix[idx]
            # query for the existance
            try:
                item = CalcSolutionMasterSpecies.objects.get(SMILES=dfi.SMILES)
                Exists = True
            except:
                item = CalcSolutionMasterSpecies.objects.create()
                Exists = False

            # insert
            if Exists:
                logging.warn('Compound %s exists in the database!' % dfi.SMILES)
                continue
            else:
                tag = ''.join([i.replace(i, self.convertDict[int(i)]) for i in str(item.id).zfill(6)])
                item.Element = '%s_%s' % (Basename, tag)
                if dfi.Charge < 0:
                    item.Species = '%s_%s%s' % (Basename, tag, str(dfi.Charge))
                elif dfi.Charge == 0:
                    item.Species = '%s_%s' % (Basename, tag)
                elif dfi.Charge > 0:
                    item.Species = '%s_%s+%s' % (Basename, tag, str(dfi.Charge))
                item.Alkalinity = dfi.Alkalinity
                item.GFWorFormula = dfi.GFWorFormula.strip('-').strip('+')
                item.GFWforElement = dfi.GFWforElement
                item.Charge = dfi.Charge
                if dfi.PubChemID > 0:
                    item.PubChemID = dfi.PubChemID
                    item.IUPACName = dfi.IUPACName
                else:
                    item.PubChemID = None
                    item.IUPACName = ''
                item.SMILES = dfi.SMILES
                item.XYZ = '%s/%s.xyz' % (xyzDir, dfi.Source)
                item.Ref_id = 1
                item.Source = dfi.Source

                item.save()
        return

    def insert_solution_species(self, csv, csvlogk):
        '''
        This functional is just help to insert solution master species. One has to double check the results manually.
        '''
        try:
            df = pd.DataFrame.from_csv(csv)
            dflogk = pd.DataFrame.from_csv(csvlogk)
        except:
            logging.warn('Failed to load the file %s or %s' % (csv, csvlogk))
            return 1


        # clean the data frame
        #df_anions = df[df.Charge < 0].drop_duplicates()
        df_anions = df[df.Reactant == 1]
        # most reduced state or primary amines
        df_anions_noH = df_anions[df_anions.Source.apply(lambda x: x.find('H') < 0)]
        df_cleaned = df_anions_noH.sort_values(by=['GFWforElement', 'IUPACName'])

        # less reduced state or secondary amines
        df_anions_wH = df_anions[df_anions.Source.apply(lambda x: x.find('H') >= 0)]
        df_2ndamines = df_anions_wH[df_anions_wH.Charge == 1]

        # insert
        for idx in df_cleaned.index.values:
            dfi = df_cleaned.ix[idx]
            # query for the existance
            try:
                obj = CalcSolutionMasterSpecies.objects.get(Source=dfi.Source)
            except:
                continue

            # create an object for solution species
            item = CalcSolutionSpecies.objects.create()
            # no protonation
            item.Reaction = '%s = %s' % (obj.Species, obj.Species)
            item.LogK = 0.0
            item.Ref_id = 1

            #item.Functional = 'M06-2X'
            #item.BasisSet = '6-31+G(d,p)'
            #item.SolvationModel = 'sSAS'

            item.save()


            # create an object for solution species
            item = CalcSolutionSpecies.objects.create()
            # first protonation
            if dfi.Charge == -1:
                item.Reaction = '%s + H+ = H%s' % (obj.Species, obj.Element)
            elif dfi.Charge == -2:
                item.Reaction = '%s + H+ = H%s-' % (obj.Species, obj.Element)
            elif dfi.Charge == 0:
                item.Reaction = '%s + H+ = H%s+' % (obj.Species, obj.Element)

            logk_calced = dflogk[dflogk.Reactants.apply(lambda x: dfi.Source in json.loads(x).keys())].Calculated.values[0]
            item.LogK = logk_calced
            item.Ref_id = 1
            item.save()

            # insert for 2nd amines
            if len(df_2ndamines) > 0:
                dfi_2nd = df_2ndamines[df_2ndamines.Source.apply(lambda x: x.split('H+')[0] == dfi.Source)]
                # find only one 2nd amine for molecule in dfi
                if len(dfi_2nd) == 1:
                    # create an object for solution species
                    item = CalcSolutionSpecies.objects.create()

                    item.Reaction = 'H%s+ + H+ = H2%s+2' % (obj.Species, obj.Element)

                    logk_calced = dflogk[dflogk.Reactants.apply(lambda x: dfi_2nd.Source.values[0] in json.loads(x).keys())].Calculated.values[0]
                    item.LogK = logk_calced
                    item.Ref_id = 1
                    item.save()

        return



if __name__ == '__main__':
    ins = insert_for_calcdata()

    # insert pKa results calculated for the Thiols
    method = 'M062X_631+Gdp_SDD_SMD_SAS_Alpha0485'
    outputDir = '%s/output/%s' % (ins.BaseDirforCalc, method)

    #Basename = 'Thiol'
    #Basename = 'Acid'
    Basename = 'Amine'
    #ReactionSet = 'logK_Namazian_w0.csv'
    ReactionSet = 'logK_Haworth_Re_w0.csv'
    csv = '%s/phreeqc/%s' % (outputDir, ReactionSet)
    csvlogk = '%s/csv/%s' % (outputDir, ReactionSet)


    relativeXYZDir = 'calcdata/data/%s/%s/xyz' % (Basename, method)
    absXYZDir = '%s/%s' % (ins.BaseDir, relativeXYZDir)

    # insert solution master species
    #ins.insert_solution_master_species(csv, Basename=Basename, xyzDir=relativeXYZDir)

    # inster solution species
    ins.insert_solution_species(csv=csv, csvlogk=csvlogk)


    # copy xyz files to the website

    try:
        os.makedirs(absXYZDir)
    except:
        pass
    df = pd.DataFrame.from_csv(csv)
    for mol in df.Source:
        shutil.copy('%s/output/%s/xyz/%s.xyz' % (ins.BaseDirforCalc, method, mol), '%s/%s.xyz' % (absXYZDir, mol))
