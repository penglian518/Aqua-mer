import numpy as np
import pandas as pd

class PhreeqcPrepare:
    def __init__(self):
        self.phreeqc = "/home/p6n/tools/phreeqc-3.3.10-12220/bin/phreeqc"
        self.tempphreeqcdat = '/home/p6n/workplace/website/cyshg/scripts/Phreeqc-scb-lg.dat'

    def genInputFile(self, obj, outdir):
        '''
        Requires not null in database!
        '''
        pHrange = np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)

        for ph in pHrange:
            fout = open('%s/pH-%s.phrq' % (outdir, str(ph)), 'w')
            # title and solution part
            fout.write('TITLE %s\n' % obj.SPTitle)
            fout.write('SOLUTION 1\n')
            fout.write('    units %s\n' % obj.SPUnit)
            fout.write('    pH %s\n' % str(ph))
            fout.write('    temp %s\n' % str(obj.SPTemperature))
            # add elements
            for ele in obj.spelements.all():
                ele_line = '    %s\t%s' % (ele.Element, str(ele.Concentration))
                if ele.PE:
                    ele_line += '\tpe'
                if ele.PPB:
                    ele_line += '\tppd %s' % ele.PPBFormula
                if ele.Others:
                    ele_line += '\t%s' % ele.Others
                fout.write('%s\n' % ele_line)
            # user defined solution_master_species
            if obj.spmaster.all():
                fout.write('SOLUTION_MASTER_SPECIES\n')
                for ms in obj.spmaster.all():
                    ms_line = '    %s\t%s\t%s\t%s' % (ms.Element, ms.Species, str(ms.Alkalinity), str(ms.GFWorFormula))
                    if ms.GFWforElement:
                        ms_line += '\t%s' % ms.GFWforElement
                    fout.write('%s\n' % ms_line)
            # user defined solution_species
            if obj.spspecies.all():
                fout.write('SOLUTION_SPECIES\n')
                for ss in obj.spspecies.all():
                    ss_line = '    %s\n        log_k\t%s\n' % (ss.Reaction, str(ss.LogK))
                    if ss.DeltaH > 0:
                        ss_line += '        delta_h\t%s %s\n' % (str(ss.DeltaH), ss.DeltaHUnits)
                    if sum([ss.AEA1, ss.AEA2, ss.AEA3, ss.AEA4, ss.AEA5 ]) > 0:
                        ss_line += '        -a_e %s %s %s %s %s\n' % (str(ss.AEA1), str(ss.AEA2), str(ss.AEA3), str(ss.AEA4), str(ss.AEA5))
                    if sum([ss.GammaA, ss.GammaB]) > 0 or ss.GammaB > 0:
                        ss_line += '        -gamma\t%s %s\n' % (str(ss.GammaA), str(ss.GammaB))
                    if ss.NoCheck:
                        ss_line += '        -no_check\n'
                    if ss.MoleBalance:
                        ss_line += '        -mole_balance\t%s\n' % str(ss.MoleBalance)
                    fout.write(ss_line)
            fout.close()
        return

    def genDatabaseFile(self, obj, outdir):
        # TODO, generate a sub-database according to user input.

        fout = open('%s/aqua-mer.dat' % outdir, 'w')
        fin = open(self.tempphreeqcdat).readlines()
        fout.writelines(fin)
        fout.close()

        return

    def genJobScript(self, obj, outdir):
        pHrange = np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)

        fout = open('%s/runPhreeqc.sh' % outdir, 'w')
        for ph in pHrange:
            cmd = '%s pH-%s.phrq pH-%s.out aqua-mer.dat' % (self.phreeqc, str(ph), str(ph))
            fout.write('%s\n' % cmd)
        fout.close()

        return

    def collectResults(self, obj, outdir):
        pHrange = np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)
        pphaser = PhreeqcParser()
        for ph in pHrange:
            phreeqcout = '%s/pH-%s.out' % (outdir, str(ph))
            df = pphaser.getSpeciesData(phreeqcout)
            if ph == obj.SPpHMin:
                df_molality_out = df[['Species']]
                df_activity_out = df[['Species']]
                df_logmolality_out = df[['Species']]
                df_logactivity_out = df[['Species']]
                df_gamma_out = df[['Species']]
                df_molev_out = df[['Species']]

            df_molality = df[['Molality']]
            df_molality.columns = [ph]
            df_molality_out = pd.concat([df_molality_out, df_molality], axis=1)

            df_activity = df[['Activity']]
            df_activity.columns = [ph]
            df_activity_out = pd.concat([df_activity_out, df_activity], axis=1)

            df_logmolality = df[['LogMolality']]
            df_logmolality.columns = [ph]
            df_logmolality_out = pd.concat([df_logmolality_out, df_logmolality], axis=1)

            df_logactivity = df[['LogActivity']]
            df_logactivity.columns = [ph]
            df_logactivity_out = pd.concat([df_logactivity_out, df_logactivity], axis=1)

            df_gamma = df[['Gamma']]
            df_gamma.columns = [ph]
            df_gamma_out = pd.concat([df_gamma_out, df_gamma], axis=1)

            df_molev = df[['moleV']]
            df_molev.columns = [ph]
            df_molev_out = pd.concat([df_molev_out, df_molev], axis=1)

        # write out the species data
        df_molality_out.to_csv('%s/phreeqc-molality.csv' % outdir)
        df_activity_out.to_csv('%s/phreeqc-activity.csv' % outdir)
        df_logmolality_out.to_csv('%s/phreeqc-logmolality.csv' % outdir)
        df_logactivity_out.to_csv('%s/phreeqc-logactivity.csv' % outdir)
        df_gamma_out.to_csv('%s/phreeqc-gamma.csv' % outdir)
        df_molev_out.to_csv('%s/phreeqc-molev.csv' % outdir)
        return




class PhreeqcParser:

    def getSpeciesData(self, phreeqcout):
        fin = open(phreeqcout).readlines()

        # find the data section
        lineindex = []
        collect_data = False
        linenumber = 0
        for line in fin:
            if line.find('----Distribution of species----') > 0:
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

        return df
