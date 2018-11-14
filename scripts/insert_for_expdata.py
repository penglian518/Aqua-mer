#!/usr/bin/env python
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
django.setup()

import pandas as pd
from expdata.models import Compound, PKA, StabilityConstants, dGsolv, Refs
from calcdata.models import CalcSolutionMasterSpecies


def insert_basicinfo(csvfile):
    # read the csv file
    df = pd.DataFrame.from_csv(csvfile)
    df.sort_values(by=['InChIKey', 'Reference1'], inplace=True)
    df.index = range(len(df))

    # gen sub dataset
    if os.path.basename(csvfile) in ['common_dGsolv.csv', 'common_repeat_dGsolv.csv']:
        df_info = df[['PubChemID', 'Formula', 'InChIKey', 'SMILES', 'IUPACName', 'AlternativeName', 'Charge',
                      'MolecularWeight_gmol-1', 'Reference2', 'Reference3']]
    elif os.path.basename(csvfile) in ['common_pKa.csv', 'common_repeat_pKa.csv']:
        df_info = df[['PubChemID', 'Formula', 'InChIKey', 'SMILES', 'IUPACName', 'AlternativeName', 'Charge',
                      'MolecularWeight_gmol-1', 'CAS_Reg_No']]

    # remove duplicates
    if len(df_info.columns) == 9:
        # pKa data
        df_info.drop_duplicates(inplace=True)
    elif len(df_info.columns) == 10:
        # dGsolv data
        # drop duplicates, 'first' mean keep freesolv ref2 and ref3 data
        df_info.drop_duplicates(subset='InChIKey', keep='first', inplace=True)
    else:
        print 'wrong df_info'
        return 1


    # insert mol one by one
    for idx in df_info.index:
        # cpd in df_info
        i_cpd = df_info.ix[idx]

        # cpds in current database
        current_cpds = Compound.objects.all()
        current_inchikeys = [i.InChIKey for i in current_cpds]

        if i_cpd['InChIKey'] in current_inchikeys:
            # get the db_cpd handle
            db_cpd = Compound.objects.get(InChIKey=i_cpd['InChIKey'])
        else:
            # gene a db_cpd handle
            db_cpd = Compound()

            # update the cpd in the database
            db_cpd.PubChemID = i_cpd['PubChemID']
            db_cpd.Formula = i_cpd['Formula']
            db_cpd.InChIKey = i_cpd['InChIKey']
            db_cpd.SMILES = i_cpd['SMILES']
            db_cpd.IUPACName = i_cpd['IUPACName']
            db_cpd.Name = i_cpd['AlternativeName']
            db_cpd.Charge = i_cpd['Charge']
            db_cpd.MolecularWeight = i_cpd['MolecularWeight_gmol-1']

        # update the CAS Source or note info
        try:
            db_cpd.CASRegNumber = i_cpd['CAS_Reg_No']
        except:
            db_cpd.Source = i_cpd['Reference2']
            db_cpd.Note = i_cpd['Reference3']

        # save to db
        db_cpd.save()


    return

def insert_refs(csvfile):
    # read the csv file
    df = pd.DataFrame.from_csv(csvfile)
    df.index = range(len(df))
    df_refs = df['Reference1']
    df_refs.drop_duplicates(inplace=True)


    # insert ref one by one
    for idx in df_refs.index:
        # ref in df_refs
        i_ref = df_refs.ix[idx]

        # transform refid
        if eval(i_ref).keys()[0] in ['CRC_0524']:
            refid = '17CRC0524'
            reference = '"Dissociation Constants of Inorganic Acids and Bases," in CRC Handbook of Chemistry and Physics, 97th Edition (Internet Version 2017), W. M. Haynes, ed., CRC Press/Taylor & Francis, Boca Raton, FL.'
        elif eval(i_ref).keys()[0] in ['CRC_0525']:
            refid = '17CRC0525'
            reference = '"Dissociation Constants of Organic Acids and Bases," in CRC Handbook of Chemistry and Physics, 97th Edition (Internet Version 2017), W. M. Haynes, ed., CRC Press/Taylor & Francis, Boca Raton, FL.'
        elif eval(i_ref).keys()[0] in ['FreeSolv2013']:
            refid = '13FreeSolv'
            reference = 'David L. Mobley, Experimental and Calculated Small Molecule Hydration Free Energies. eScholarship. Version 0.32.'
        elif eval(i_ref).keys()[0] in ['MNSol2012']:
            refid = '12MNSol'
            reference = 'Marenich et al., Minnesota Solvation Database-version 2012.'
        elif eval(i_ref).keys()[0] in ['Rizzo2006']:
            refid = '06RACK'
            reference = 'Rizzo et al., J. Chem. Theory Comput., 2006, 2(1) 128-139.'
        elif eval(i_ref).keys()[0] in ['Marenich2009']:
            refid = '09MCT'
            reference = 'Marenich et al., J. Phys. Chem. B, 2009, 113 (18) 6378-6396.'


        # refs in current database
        current_refs = Refs.objects.all()
        current_refids = [i.RefID for i in current_refs]

        if refid not in current_refids:
            db_ref = Refs()

            # update refs in db
            db_ref.RefID = refid
            db_ref.Reference = reference

            # save to db
            db_ref.save()

    return

def insert_dgsolvs(csvfile):
    # read the csv file
    df = pd.DataFrame.from_csv(csvfile)
    df.index = range(len(df))
    df_dgsolvs = df[['InChIKey', 'dG_solvation_kcalmol-1', 'Reference1']]
    df_dgsolvs.drop_duplicates(inplace=True)


    # insert dgsolv one by one
    for idx in df_dgsolvs.index:
        # ref in df_dgsolv
        i_dgsolv = df_dgsolvs.ix[idx]

        # transform refid
        if eval(i_dgsolv['Reference1']).keys()[0] in ['CRC_0524']:
            refid = '17CRC0524'
        elif eval(i_dgsolv['Reference1']).keys()[0] in ['CRC_0525']:
            refid = '17CRC0525'
        elif eval(i_dgsolv['Reference1']).keys()[0] in ['FreeSolv2013']:
            refid = '13FreeSolv'
        elif eval(i_dgsolv['Reference1']).keys()[0] in ['MNSol2012']:
            refid = '12MNSol'
        elif eval(i_dgsolv['Reference1']).keys()[0] in ['Rizzo2006']:
            refid = '06RACK'
        elif eval(i_dgsolv['Reference1']).keys()[0] in ['Marenich2009']:
            refid = '09MCT'


        # refs in current database
        current_dgsolvs = dGsolv.objects.all()
        current_inchikeys = [i.MolID.InChIKey for i in current_dgsolvs]

        # if new molecule, save the dGsolv value; else if new dGsolv value, save it, otherwise ignore
        if i_dgsolv['InChIKey'] not in current_inchikeys:
            db_dgsolv = dGsolv()

            # update refs in db
            db_dgsolv.MolID = Compound.objects.get(InChIKey=i_dgsolv['InChIKey'])
            db_dgsolv.dGsolv = i_dgsolv['dG_solvation_kcalmol-1']
            db_dgsolv.dGsolvReference = Refs.objects.get(RefID=refid)

            # save to db
            db_dgsolv.save()
        else:
            # fingerprint for incoming cpd
            i_dgsolv_fingerprint = '%s%s%s' % (str(i_dgsolv['InChIKey']), str(float(i_dgsolv['dG_solvation_kcalmol-1'])), refid)

            db_cpd = Compound.objects.get(InChIKey=i_dgsolv['InChIKey'])
            db_cpd_dgsolvs = dGsolv.objects.filter(MolID=db_cpd)

            # all dGsolv values for this cpd
            db_dgsolv_fingerprint_sets = []
            for d in db_cpd_dgsolvs:
                d_fingerprint = '%s%s%s' % (str(i_dgsolv['InChIKey']), str(float(d.dGsolv)), str(d.dGsolvReference.RefID))
                db_dgsolv_fingerprint_sets.append(d_fingerprint)

            # if new value, save it
            if i_dgsolv_fingerprint not in db_dgsolv_fingerprint_sets:
                db_dgsolv = dGsolv()

                # update refs in db
                db_dgsolv.MolID = Compound.objects.get(InChIKey=i_dgsolv['InChIKey'])
                db_dgsolv.dGsolv = i_dgsolv['dG_solvation_kcalmol-1']
                db_dgsolv.dGsolvReference = Refs.objects.get(RefID=refid)

                # save to db
                db_dgsolv.save()

    return

def insert_pKas(csvfile):
    # read the csv file
    df = pd.DataFrame.from_csv(csvfile)
    df.index = range(len(df))
    df_pkas = df[['InChIKey', 'pKa_Step', 'pKa_Temperature_C', 'pKa', 'Reference1']]
    df_pkas.drop_duplicates(inplace=True)

    # insert dgsolv one by one
    for idx in df_pkas.index:
        # ref in df_pkas
        i_pka = df_pkas.ix[idx]

        # transform refid
        if eval(i_pka['Reference1']).keys()[0] in ['CRC_0524']:
            refid = '17CRC0524'
        elif eval(i_pka['Reference1']).keys()[0] in ['CRC_0525']:
            refid = '17CRC0525'
        elif eval(i_pka['Reference1']).keys()[0] in ['FreeSolv2013']:
            refid = '13FreeSolv'
        elif eval(i_pka['Reference1']).keys()[0] in ['MNSol2012']:
            refid = '12MNSol'

        # determine species
        Total_records = len(df_pkas[df_pkas.InChIKey == i_pka['InChIKey']])
        speciesH = Total_records + 1 - i_pka['pKa_Step']
        speciesL = 1
        if speciesH > 1:
            species = 'H%dL' % speciesH
        else:
            species = 'HL'

        # refs in current database
        current_pkas = PKA.objects.all()
        current_inchikeys = [i.MolID.InChIKey for i in current_pkas]

        if i_pka['InChIKey'] in current_inchikeys:
            # get the compound id in the database
            cpd_id = Compound.objects.filter(InChIKey=i_pka['InChIKey'])[0].id
            # get the exist pKa records for this compound
            exist_pkas = PKA.objects.filter(MolID_id=cpd_id)
            # get the exist pKa species for this compound
            exist_speciess = [p.Species for p in exist_pkas]

            if species not in exist_speciess:
                db_pka = PKA()

                # update refs in db
                db_pka.MolID = Compound.objects.get(InChIKey=i_pka['InChIKey'])
                db_pka.H = speciesH
                db_pka.L = speciesL
                db_pka.TemperatureC = i_pka['pKa_Temperature_C']
                if refid == '17CRC0524':
                    db_pka.IonicStrength = 0.00
                db_pka.pKa = i_pka['pKa']
                db_pka.pKaReference = Refs.objects.get(RefID=refid)

                # save to db
                db_pka.save()
        else:
            db_pka = PKA()

            # update refs in db
            db_pka.MolID = Compound.objects.get(InChIKey=i_pka['InChIKey'])
            db_pka.H = speciesH
            db_pka.L = speciesL
            db_pka.TemperatureC = i_pka['pKa_Temperature_C']
            if refid == '17CRC0524':
                db_pka.IonicStrength = 0.00
            db_pka.pKa = i_pka['pKa']
            db_pka.pKaReference = Refs.objects.get(RefID=refid)

            # save to db
            db_pka.save()

    return


def update_phrname_from_caldata():
    '''
    Will try to update phrname according to PubChem ID of molecules in caldata.
    '''

    exp_cpds = Compound.objects.all()
    calc_cpds = CalcSolutionMasterSpecies.objects.all()

    for i_cpd in exp_cpds:
        try:
            i_cpd_calc = CalcSolutionMasterSpecies.objects.get(PubChemID=i_cpd.PubChemID)
        except:
            i_cpd_calc= ''

        if type(i_cpd_calc) in [CalcSolutionMasterSpecies]:
            i_cpd.PhrName = i_cpd_calc.Element
            i_cpd.save()
        elif type(i_cpd_calc) in [django.db.models.query.QuerySet]:
            print('%d compounds found in Calcdata have the PubChemID %d! Compund name in Expdata is %s' % (len(i_cpd_calc), i_cpd.PubChemID, i_cpd.Name))

    return


def main():
    pka_csv = '/home/p6n/workplace/doc/combined/common_pKa.csv'
    dgsolv_csv = '/home/p6n/workplace/doc/combined/common_dGsolv.csv'

    # insert basic info
    #insert_basicinfo(pka_csv)
    #insert_basicinfo(dgsolv_csv)

    # insert refs
    #insert_refs(pka_csv)
    #insert_refs(dgsolv_csv)

    # insert dGsolv
    #insert_dgsolvs(dgsolv_csv)

    # insert_pKas
    insert_pKas(pka_csv)

def main_repeat():
    pka_csv = '/home/p6n/workplace/doc/combined/common_repeat_pKa.csv'
    dgsolv_csv = '/home/p6n/workplace/doc/combined/common_repeat_dGsolv.csv'

    # insert basic info
    #insert_basicinfo(pka_csv)
    #insert_basicinfo(dgsolv_csv)

    # insert refs
    #insert_refs(pka_csv)
    #insert_refs(dgsolv_csv)

    # insert dGsolv
    #insert_dgsolvs(dgsolv_csv)

    # insert_pKas
    insert_pKas(pka_csv)

if __name__ == '__main__':
    #main()
    #main_repeat()
    update_phrname_from_caldata()