import numpy as np
import pandas as pd
import shutil, os


class PhreeqcPrepare:
    def __init__(self):
        self.phreeqc = "/home/p6n/tools/phreeqc-3.3.10-12220/bin/phreeqc"
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


    def genInputFile(self, obj, outdir):
        '''
        Requires not null in database!
        '''
        pHrange = list(np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)) + [obj.SPpHMax]
        pHrange = [round(i, 2) for i in pHrange]

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
                # clean up
                self.clean_default_values(obj=obj, type='master')
                fout.write('SOLUTION_MASTER_SPECIES\n')
                for ms in obj.spmaster.all():
                    ms_line = '    %s\t%s\t%s\t%s' % (ms.Element, ms.Species, str(ms.Alkalinity), str(ms.GFWorFormula))
                    if ms.GFWforElement:
                        ms_line += '\t%s' % ms.GFWforElement
                    fout.write('%s\n' % ms_line)
            # user defined solution_species
            if obj.spspecies.all():
                # clean up
                self.clean_default_values(obj=obj, type='species')

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
        pHrange = list(np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)) + [obj.SPpHMax]
        pHrange = [round(i, 2) for i in pHrange]

        fout = open('%s/runPhreeqc.sh' % outdir, 'w')
        for ph in pHrange:
            cmd = '%s pH-%s.phrq pH-%s.out aqua-mer.dat' % (self.phreeqc, str(ph), str(ph))
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
        pHrange = list(np.arange(obj.SPpHMin, obj.SPpHMax, obj.SPpHIncrease)) + [obj.SPpHMax]
        pHrange = [round(i, 2) for i in pHrange]
        pphaser = PhreeqcParser()
        columns = ['Species']
        df_out = pd.DataFrame()

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

        dir_download = '%s-%d' % ('hgspeci', obj.JobID)
        try:
            os.makedirs(dir_download)
        except:
            pass
        shutil.copy(outfile, '%s/%s/' % (outdir, dir_download))

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
        df = df.drop_duplicates()

        return df
