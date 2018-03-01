#!/usr/bin/env python
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
django.setup()

import pandas as pd
from calcdata.models import CalcSolutionMasterSpecies, CalcSolutionSpecies, Refs


class insert_for_calcdata:
    def __init__(self):
        self.BaseDirforCalc = '/home/p6n/workplace/mercury_complex'

    def insert_solution_master_species(self, csv):
        df = pd.DataFrame.from_csv(csv)

        # clean the data frame

        # query for the existance

        # insert


        return

    def insert_solution_species(self):
        return



if __name__ == '__main__':
    ins = insert_for_calcdata()
    method = 'M062X_631+Gdp_SDD_SMD_SAS_Alpha0485'
    outputDir = '%s/output/%s' % (ins.BaseDirforCalc, method)
    csv = '%s/phreeqc/properties.csv' % outputDir

    ins.insert_solution_master_species(csv)