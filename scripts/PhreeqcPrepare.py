import numpy as np
import pandas as pd
import shutil, os

from phreeqcdb.models import SolutionMasterSpecies, SolutionSpecies, Phases, ExchangeMasterSpecies, ExchangeSpecies, \
    SurfaceMasterSpecies, SurfaceSpecies, Rates
from calcdata.models import CalcSolutionMasterSpecies, CalcSolutionSpecies
from django.db.models import Q
from hgspeci.models import HgSpeciJob

class PhreeqcPrepare:
    def __init__(self):
        self.phreeqc = "/home/p6n/tools/phreeqc-3.4.0-12927/bin/phreeqc"
        self.tempphreeqcdat = '/home/p6n/workplace/website/cyshg/scripts/Phreeqc-scb-lg.dat'

    def clean_default_values(self, obj, type='species'):
        if type in ['Species', 'species']:
            for ss in obj.spspecies.all():
                if ss.LogK == None:
                    ss.LogK = 0.0
                if ss.DeltaH == None:
                    ss.DeltaH = 0.0
                if ss.AEA1 == None:
                    ss.AEA1 = 0.0
                if ss.AEA2 == None:
                    ss.AEA2 = 0.0
                if ss.AEA3 == None:
                    ss.AEA3 = 0.0
                if ss.AEA4 == None:
                    ss.AEA4 = 0.0
                if ss.AEA5 == None:
                    ss.AEA5 = 0.0
                if ss.AEA6 == None:
                    ss.AEA6 = 0.0
                if ss.GammaA == None:
                    ss.GammaA = 0.0
                if ss.GammaB == None:
                    ss.GammaB = 0.0
                ss.save()
        if type in ['master', 'Master']:
            for ms in obj.spmaster.all():
                if ms.Alkalinity == None:
                    ms.Alkalinity = 0.0
                if ms.GFWorFormula == None:
                    ms.GFWforElement = 0.0
                if ms.GFWforElement == None:
                    ms.GFWforElement = 0.0
                ms.save()
        obj.save()

    def format_elements_input(self, ele):
        ele_line = '    %s\t%s' % (ele.Element, str(ele.Concentration))
        if ele.Unit:
            ele_line += '\t%s' % ele.Unit
        if ele.AS and ele.ASFormula:
            ele_line += '\tas %s' % ele.ASFormula
        if ele.GFW and ele.GFWFormula:
            ele_line += '\tgfw %s' % ele.GFWFormula
        if ele.Redox:
            ele_line += '\t%s' % ele.Redox
        if ele.Others:
            ele_line += '\t%s' % ele.Others
        ele_line += '\n'
        return ele_line


    def format_solution_master_species(self, ms):
        ms_line = '    %s\t%s\t%s\t%s' % (ms.Element, ms.Species, str(ms.Alkalinity), str(ms.GFWorFormula))
        if ms.GFWforElement:
            ms_line += '\t%s' % ms.GFWforElement
        ms_line += '\n'
        return ms_line

    def format_species(self, ss):
        ''' for solution species '''
        ss_line = '%s\n' % ss.Reaction
        # log K
        try:
            condition = abs(ss.LogK) > 0
        except:
            condition = False

        if condition:
            #ss_line += '        -delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
            ss_line += '    -log_k\t%s\n' % str(ss.LogK)
        # delta
        try:
            condition = abs(ss.DeltaH) > 0
        except:
            condition = False

        if condition:
            ss_line += '    -delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
        # AE
        try:
            condition = sum(abs(i) for i in [ss.AEA1, ss.AEA2, ss.AEA3, ss.AEA4, ss.AEA5, ss.AEA6]) > 0
        except:
            condition = False
        if condition:
            ss_line += '    -analytical %s %s %s %s %s %s\n' % (
            str(ss.AEA1), str(ss.AEA2), str(ss.AEA3), str(ss.AEA4), str(ss.AEA5), str(ss.AEA6))
        # gamma
        try:
            condition = sum(abs(i) for i in [ss.GammaA, ss.GammaB]) > 0 or ss.GammaB > 0
        except:
            condition = False
        if condition:
            ss_line += '    -gamma\t%s %s\n' % (str(ss.GammaA), str(ss.GammaB))
        # dw
        try:
            condition = sum(abs(i) for i in [ss.DW1, ss.DW2, ss.DW3, ss.DW4]) > 0
        except:
            condition = False
        if condition:
            ss_line += '    -dw %s %s %s %s\n' % (
            str(ss.DW1), str(ss.DW2), str(ss.DW3), str(ss.DW4))
        # Vm
        try:
            condition = sum(abs(i) for i in [ss.VM1, ss.VM2, ss.VM3, ss.VM4, ss.VM5, ss.VM6, ss.VM7, ss.VM8, ss.VM9, ss.VM10]) > 0
        except:
            condition = False
        if condition:
            ss_line += '    -Vm %s %s %s %s %s %s %s %s %s %s\n' % (
            str(ss.VM1), str(ss.VM2), str(ss.VM3), str(ss.VM4), str(ss.VM5),
            str(ss.VM6), str(ss.VM7), str(ss.VM8), str(ss.VM9), str(ss.VM10),
            )

        if ss.NoCheck:
            ss_line += '    -no_check\n'
        if ss.MoleBalance:
            ss_line += '    -mole_balance\t%s\n' % str(ss.MoleBalance)
        return ss_line

    def format_phases(self, ss):
        ss_line = '%s\n' % ss.PhaseName

        ss_line += '    %s\n' % ss.Reaction
        # log K
        try:
            condition = abs(ss.LogK) > 0
        except:
            condition = False

        if condition:
            #ss_line += '        -delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
            ss_line += '        -log_k\t%s\n' % str(ss.LogK)
        # delta
        try:
            condition = abs(ss.DeltaH) > 0
        except:
            condition = False

        if condition:
            ss_line += '        -delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
        # AE
        try:
            condition = sum(abs(i) for i in [ss.AEA1, ss.AEA2, ss.AEA3, ss.AEA4, ss.AEA5, ss.AEA6]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -analytical %s %s %s %s %s %s\n' % (
            str(ss.AEA1), str(ss.AEA2), str(ss.AEA3), str(ss.AEA4), str(ss.AEA5), str(ss.AEA6))
        # gamma
        try:
            condition = sum(abs(i) for i in [ss.GammaA, ss.GammaB]) > 0 or ss.GammaB > 0
        except:
            condition = False
        if condition:
            ss_line += '        -gamma\t%s %s\n' % (str(ss.GammaA), str(ss.GammaB))
        # dw
        try:
            condition = sum(abs(i) for i in [ss.DW1, ss.DW2, ss.DW3, ss.DW4]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -dw %s %s %s %s\n' % (
            str(ss.DW1), str(ss.DW2), str(ss.DW3), str(ss.DW4))
        # Vm
        try:
            condition = sum(abs(i) for i in [ss.VM1, ss.VM2, ss.VM3, ss.VM4, ss.VM5, ss.VM6, ss.VM7, ss.VM8, ss.VM9, ss.VM10]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -Vm %s %s %s %s %s %s %s %s %s %s\n' % (
            str(ss.VM1), str(ss.VM2), str(ss.VM3), str(ss.VM4), str(ss.VM5),
            str(ss.VM6), str(ss.VM7), str(ss.VM8), str(ss.VM9), str(ss.VM10),
            )

        # Tc
        try:
            condition = sum(abs(i) for i in [ss.TC]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -T_c\t%s\n' % str(ss.TC)
        # Pc
        try:
            condition = sum(abs(i) for i in [ss.PC]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -P_c\t%s\n' % str(ss.PC)
        # Omega
        try:
            condition = sum(abs(i) for i in [ss.OMEGA]) > 0
        except:
            condition = False
        if condition:
            ss_line += '        -Omega\t%s\n' % str(ss.OMEGA)

        return ss_line

    def format_exchange_species(self, ss):
        ss_line = '    %s\n        log_k\t%s\n' % (ss.Reaction, str(ss.LogK))
        if ss.DeltaH > 0:
            ss_line += '        delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
        if sum([ss.GammaA, ss.GammaB]) > 0 or ss.GammaB > 0:
            ss_line += '        -gamma\t%s %s\n' % (str(ss.GammaA), str(ss.GammaB))
        if ss.Davies:
            ss_line += '        -davies\n'
        return ss_line

    def format_surface_species(self, ss):
        ss_line = '    %s\n        log_k\t%s\n' % (ss.Reaction, str(ss.LogK))
        return ss_line

    def genQueryStr(self, obj, type='', string='', string_calc=''):
        """
        :param obj: HgSpeciJob object
        :param type: ['Element', 'SolutionMasterSpecies', 'SolutionSpecies']
        :param string: 'element', 'species' form phreeqcdb
        :param string: 'element', 'species' form calcdatabase
        :return: query_str (for phreeqcdb)
        :return: query_str_calc (for calcdatabase)
        """
        query_str, query_str_calc = '', ''

        SelectedDB = obj.SPDBtoUse

        if type in ['Element']:
            ele = string
            # genearte the query string.
            if SelectedDB in ['phreeqc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Element__istartswith='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['aquamer']:
                query_str = "Q(DBSource__DBID='Aquamer_default') & Q(Element__istartswith='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+aquamer']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Element__istartswith='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+calc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Element__istartswith='%s')" % ele
                query_str_calc = "Q(Element__istartswith='%s')" % ele
            elif SelectedDB in ['phreeqc+aquamer+calc']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Element__istartswith='%s')" % ele
                query_str_calc = "Q(Element__istartswith='%s')" % ele
        elif type in ['SolutionMasterSpecies']:
            ele = string
            # genearte the query string.
            if SelectedDB in ['phreeqc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Element='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['aquamer']:
                query_str = "Q(DBSource__DBID='Aquamer_default') & Q(Element='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+aquamer']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Element='%s')" % ele
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+calc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Element='%s')" % ele
                query_str_calc = "Q(Element='%s')" % ele
            elif SelectedDB in ['phreeqc+aquamer+calc']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Element='%s')" % ele
                query_str_calc = "Q(Element='%s')" % ele
        elif type in ['SolutionSpecies']:
            master_species = string
            master_calc_species = string_calc
            # genearte the query string.
            if SelectedDB in ['phreeqc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Reaction__contains='%s')" % master_species
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['aquamer']:
                query_str = "Q(DBSource__DBID='Aquamer_default') & Q(Reaction__contains='%s')" % master_species
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+aquamer']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Reaction__contains='%s')" % master_species
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+calc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') & Q(Reaction__contains='%s')" % master_species
                query_str_calc = "Q(Reaction__contains='%s')" % master_calc_species
            elif SelectedDB in ['phreeqc+aquamer+calc']:
                query_str = "(Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')) & Q(Reaction__contains='%s')" % master_species
                query_str_calc = "Q(Reaction__contains='%s')" % master_calc_species
        elif type in ['ByDB']:
            # genearte the query string.
            if SelectedDB in ['phreeqc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default')"
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['aquamer']:
                query_str = "Q(DBSource__DBID='Aquamer_default')"
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+aquamer']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')"
                query_str_calc = "Q(id__lt=0)"
            elif SelectedDB in ['phreeqc+calc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default')"
                query_str_calc = "Q(id__gt=0)"
            elif SelectedDB in ['phreeqc+aquamer+calc']:
                query_str = "Q(DBSource__DBID='Phreeqc_default') | Q(DBSource__DBID='Aquamer_default')"
                query_str_calc = "Q(id__gt=0)"

        return query_str, query_str_calc

    def genpHRange(self, obj):
        if obj.SPpHMax <= obj.SPpHMin:
            pHrange = [round(obj.SPpHMin, 2)]
        elif obj.SPpHIncrease == 0:
            pHrange = [round(obj.SPpHMin, 2), round(obj.SPpHMax, 2)]
        else:
            pHrange = list(np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)) + [obj.SPpHMax]
            pHrange = [round(i, 2) for i in pHrange]
        return pHrange

    def genInputFile(self, obj, outdir):
        '''
        Requires not null in database!
        '''

        if str(obj.SPUserDefinedInput) != '':
            fout = open('%s/userdefined.phrq' % outdir, 'w')
            fout.write(obj.SPUserDefinedInput)
            fout.write('\n')
            fout.close()
            return


        pHrange = self.genpHRange(obj=obj)

        for ph in pHrange:
            fout = open('%s/pH-%s.phrq' % (outdir, str(ph)), 'w')
            # title and solution part
            fout.write('TITLE %s\n' % obj.SPTitle)
            fout.write('SOLUTION 1\n')
            fout.write('    units %s\n' % obj.SPUnit)
            #fout.write('    pH %s\n' % str(ph))
            #fout.write('    pH %s\n' % str(7.0))
            if obj.SPTitrant in ['NaOH']:
                fout.write('    pH %s\n' % str(obj.SPpHMin))
            elif obj.SPTitrant in ['HCl', 'HNO3', 'H2SO4', 'H2S']:
                fout.write('    pH %s\n' % str(obj.SPpHMax))

            if obj.SPRedoxMethod in ['pe']:
                fout.write('    pe %s\n' % str(obj.SPRedoxValue))
            elif obj.SPRedoxMethod in ['couple', 'Redox Couple']:
                fout.write('    redox %s\n' % str(obj.SPRedoxValue))
            fout.write('    temp %s\n' % str(obj.SPTemperature))
            # add elements
            for ele in obj.spelements.all():
                ele_line = self.format_elements_input(ele)
                fout.write(ele_line)
            # user defined solution_master_species
            if obj.spmaster.all():
                # clean up
                self.clean_default_values(obj=obj, type='master')
                fout.write('SOLUTION_MASTER_SPECIES\n')
                for ms in obj.spmaster.all():
                    ms_line = self.format_solution_master_species(ms)
                    fout.write(ms_line)
            # user defined solution_species
            if obj.spspecies.all():
                # clean up
                self.clean_default_values(obj=obj, type='species')

                fout.write('SOLUTION_SPECIES\n')
                for ss in obj.spspecies.all():
                    ss_line = self.format_species(ss)
                    fout.write(ss_line)

            # add additional phase section.
            fout.write('\n')
            fout.write('PHASES\n')
            fout.write('Fix_H+\n')
            fout.write('    H+ = H+\n')
            fout.write('    log_k 0.0\n')
            fout.write('\n')
            fout.write('EQUILIBRIUM_PHASES 1\n')
            fout.write('    Fix_H+   -%s   %s    %.1f\n' % (str(ph), obj.SPTitrant, obj.SPTitrantConcentration))
            fout.write('\n')

            fout.close()
        return

    def genDatabaseFile(self, obj, outdir):
        # TODO, generate a sub-database according to user input.

        # init output_line
        output_line = ''

        ## prepare Solution_master_species
        # get all elements in this job
        elements = [ele.Element for ele in obj.spelements.all()]
        # get related solution master species objs
        #ms_obj_phreeqcdb = [ele for ele in SolutionMasterSpecies.objects.filter(Element__in=elements)]
        #### remove this exclued_ms, when added Solution_Species for this species!!!!
        #exclued_ms = ["U+4", "S2O3-2", "L-", "Co+2", "Ni+2", "Dom-4", "Citrate-3", "Rcoo-", "Edta-4", "UO2+2", "Co+3", "Cdta-4"]
        #ms_obj_phreeqcdb = [i for i in SolutionMasterSpecies.objects.all() if i.Species]
        #ms_obj_calcdata = [ele for ele in CalcSolutionMasterSpecies.objects.filter(Element__in=elements)]

        query_str, query_str_calc = self.genQueryStr(obj, type='ByDB')
        ms_obj_phreeqcdb = list(SolutionMasterSpecies.objects.filter(eval(query_str)))
        ms_obj_calcdata = list(CalcSolutionMasterSpecies.objects.filter(eval(query_str_calc)))

        # generate the Solution_Master_Species data block
        output_line += 'SOLUTION_MASTER_SPECIES\n'
        for ms in ms_obj_phreeqcdb + ms_obj_calcdata:
            ms_line = self.format_solution_master_species(ms)
            output_line += ms_line

        ## prepare solution species
        # get species
        #species_phreeqcdb = [ele.Species for ele in ms_obj_phreeqcdb]
        species_calcdata = [ele.Species for ele in ms_obj_calcdata]
        # get species objs
        #ss_obj_phreeqcdb = list(SolutionSpecies.objects.all())
        ss_obj_phreeqcdb = list(SolutionSpecies.objects.filter(eval(query_str)))
        ss_obj_calcdata = []
        #for ele in species_phreeqcdb:
        #    ss_obj_phreeqcdb += list(SolutionSpecies.objects.filter(Reaction__contains = ele))
        for ele in species_calcdata:
            ss_obj_calcdata += list(CalcSolutionSpecies.objects.filter(Reaction__contains=ele))
        # generate the Solution_Species data block
        output_line += 'SOLUTION_SPECIES\n'
        for ss in ss_obj_phreeqcdb + ss_obj_calcdata:
            ss_line = self.format_species(ss)
            output_line += ss_line

        ## prepare PHASES
        # get phases objs
        ps_obj_phreeqcdb = list(Phases.objects.filter(eval(query_str)))
        #for ele in species_phreeqcdb:
        #    ss_obj_phreeqcdb += list(Phases.objects.filter(Reaction__contains = ele))
        # genearte the PHASES data block
        output_line += 'PHASES\n'
        for ps in ps_obj_phreeqcdb:
            try:
                ps_line = self.format_phases(ps)
            except Exception as e:
                print e
                ps_line = '\n'
            output_line += ps_line

        ## prepare Exchange_master_species
        output_line += 'EXCHANGE_MASTER_SPECIES\n'
        for ex in ExchangeMasterSpecies.objects.filter(eval(query_str)):
            output_line += '    %s  %s\n' % (ex.ExchangeName, ex.ExchangeMaster)

        ## prepare Exchange_species
        output_line += 'EXCHANGE_SPECIES\n'
        for ex in ExchangeSpecies.objects.filter(eval(query_str)):
            ex_line = self.format_exchange_species(ex)
            output_line += ex_line

        ## prepare Surface_master_species
        output_line += 'SURFACE_MASTER_SPECIES\n'
        for ex in SurfaceMasterSpecies.objects.filter(eval(query_str)):
            output_line += '    %s  %s\n' % (ex.BindingSite, ex.SurfaceMaster)

        ## prepare Surface_species
        output_line += 'SURFACE_SPECIES\n'
        for ex in SurfaceSpecies.objects.filter(eval(query_str)):
            ex_line = self.format_surface_species(ex)
            output_line += ex_line

        ## prepare RATES
        output_line += 'RATES\n'
        for ex in Rates.objects.filter(eval(query_str)):
            ex_line = '%s\n%s\n' % (ex.Name, ex.BasicStatement)
            output_line += ex_line

        ## save to database file
        fout = open('%s/aqua-mer.dat' % outdir, 'w')
        fout.write(output_line)
        fout.close()

        return

    def genJobScript(self, obj, outdir):
        if str(obj.SPUserDefinedInput) != '':
            fout = open('%s/runPhreeqc.sh' % outdir, 'w')
            cmd = '''if [ -f userdefined.phrq -a -f aqua-mer.dat ]; then %s userdefined.phrq userdefined.out aqua-mer.dat; fi''' \
                  % (self.phreeqc)
            fout.write('%s\n' % cmd)
            fout.close()
            return

        pHrange = self.genpHRange(obj=obj)
        fout = open('%s/runPhreeqc.sh' % outdir, 'w')
        for ph in pHrange:
            #cmd = '%s pH-%s.phrq pH-%s.out aqua-mer.dat' % (self.phreeqc, str(ph), str(ph))
            cmd = '''if [ -f pH-%s.phrq -a -f aqua-mer.dat ]; then %s pH-%s.phrq pH-%s.out aqua-mer.dat; fi''' \
                  % (str(ph), self.phreeqc, str(ph), str(ph))
            fout.write('%s\n' % cmd)
        fout.close()

        return

    def collectResults(self, obj, outdir):
        for t in ['Molality', 'Activity', 'LogMolality', 'LogActivity', 'Gamma']:
            try:
                self.collectResultsfromPhreeqc(obj=obj, outdir=outdir, datatype=t)
            except Exception as e:
                print 'Failed to extract %s data from phreeqc output file!\n%s\n' % (t, e)
        return

    def collectResultsfromPhreeqc(self, obj, outdir, datatype='molality'):
        pHrange = self.genpHRange(obj=obj)

        pphaser = PhreeqcParser()
        columns = ['Species']
        df_out = pd.DataFrame()

        # prepare download dir
        dir_download = '%s-%d' % ('hgspeci', obj.JobID)
        try:
            os.makedirs(dir_download)
        except:
            pass

        # collect result to generate csv file
        try:
            for ph in pHrange:
                phreeqcout = '%s/pH-%s.out' % (outdir, str(ph))
                df = pphaser.getSpeciesData(phreeqcout)
                df_column = pd.DataFrame()
                columns += [ph]

                if ph == obj.SPpHMin:
                    df_out = df[['Species']]

                if datatype.lower() in ['molality']:
                    df_column = df[['Species', 'Molality']]
                if datatype.lower() in ['activity']:
                    df_column = df[['Species', 'Activity']]
                if datatype.lower() in ['logmolality']:
                    df_column = df[['Species', 'LogMolality']]
                if datatype.lower() in ['logactivity']:
                    df_column = df[['Species', 'LogActivity']]
                if datatype.lower() in ['gamma']:
                    df_column = df[['Species', 'Gamma']]
                if datatype.lower() in ['molev']:
                    df_column = df[['Species', 'moleV']]

                df_out = df_out.merge(df_column, how='left', on='Species')
            df_out.columns = columns

            # write out the species data
            outfile = '%s/speciation-%s.csv' % (outdir, datatype.lower())
            df_out.to_csv(outfile)

            # copy csv files to download dir
            shutil.copy(outfile, '%s/%s/' % (outdir, dir_download))
        except:
            pass

        # collect data for downloading
        # input & output files
        for ph in pHrange:
            f_input = '%s/pH-%s.phrq' % (outdir, str(ph))
            f_output = '%s/pH-%s.out' % (outdir, str(ph))

            try:
                shutil.copy(f_input, '%s/%s/' % (outdir, dir_download))
                shutil.copy(f_output, '%s/%s/' % (outdir, dir_download))
            except:
                pass

        if str(obj.SPUserDefinedInput) != '':
            for f in os.listdir(outdir):
                if f not in ['aqua-mer.dat', 'phreeqc.log', 'runPhreeqc.sh']:
                    try:
                        shutil.copy('%s/%s' % (outdir, f), '%s/%s/' % (outdir, dir_download))
                    except:
                        pass
        return



class PhreeqcParser:

    def getSpeciesData(self, phreeqcout):
        fin = open(phreeqcout).readlines()

        # find the data section
        lineindex = []
        collect_data = False
        linenumber = 0

        section_order = 1
        for line in fin:
            if line.find('----Distribution of species----') > 0 and section_order == 1:
                section_order += 1
            elif line.find('----Distribution of species----') > 0 and section_order == 2:
                collect_data = True
                lineindex.append(linenumber)

            if collect_data and len(line) == 1:
                lineindex.append(linenumber)

            linenumber += 1

        # get rawdata
        if len(lineindex) >= 4:
            rawdata = fin[lineindex[2]:lineindex[3]]
        else:
            print 'Can not find the data section from the file %s' % phreeqcout
            return 1

        # get all the species data
        species = [l.strip().split() for l in rawdata if l.startswith(' ')]
        df = pd.DataFrame(species)
        df.columns = ['Species', 'Molality', 'Activity', 'LogMolality', 'LogActivity', 'Gamma', 'moleV']
        df = df.drop_duplicates()

        return df
