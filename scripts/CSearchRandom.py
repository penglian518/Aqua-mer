#!/usr/bin/env python
#
# @purpose
#   to perform a conformation search with randomly single bond rotation and DBScan clustering
#
# @Author Peng Lian
# @Email penglian518@gmail.com
# @Date Mar 9 2017
#

import subprocess, os, time, random, logging, argparse, shutil

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt



class CSearchRand:
    def __init__(self):

        self.debug = True

        self.NRotamers = 1000
        self.Forcefield = 'UFF'
        self.NStep = 2500
        self.Opt = 'sd'
        self.eps = 0.03
        self.minSamples = 1
        self.outPrefix = '_l_Xe_r_'

        self.obabel = '/home/p6n/anaconda2/bin/obabel'
        self.obrotamer = '/home/p6n/anaconda2/bin/obrotamer'
        self.obminimize = '/home/p6n/anaconda2/bin/obminimize'
        self.rdkitrotamer = '/home/p6n/tools/myPythonLib/PLg09/rdkitrotamer.py'
        self.vmd = '/home/p6n/tools/vmd-1.9.2/bin/vmd'


    def genRotamers(self, inMol2, outMol2, debug=True):
        '''

        Using openbabel as the work horse for rotamer generating

        :param inMol2:
        :param outMol2: Should be in mol2 or sdf file. Becasue obminimize could not handle multiple structures in pdf
        :return:
        '''

        if debug:
            logging.info('-' * 50)
            logging.info('Run: genRotamers(inMol2=%s, outMol2=%s, debug=%s)\n' % (inMol2, outMol2, debug))

        # delete the exist mol2
        try:
            os.remove(outMol2)
        except:
            pass

        # command
        cmd = '%s %s >> %s' % (self.obrotamer, inMol2, outMol2)
        if debug:
            logging.info('Running: %s\n' % cmd)

        # generate rotamers
        counter = 0
        Info = []
        while counter < self.NRotamers:
            #subprocess.Popen(cmd, shell=True).wait()
            rotcmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            # grab output and error
            roterr, rotout = rotcmd.communicate()
            Info.append(rotout)

            counter += 1
        logging.info(list(set(Info))[0])

    def genRotamers_rdkit(self, inMol2, outMol2, debug=True):
        '''

        Using rdkit as the work horse for rotamer generating

        :param inMol2:
        :param outMol2: Should be in mol2 or sdf file. Becasue obminimize could not handle multiple structures in pdf
        :return:
        '''

        if debug:
            logging.info('-' * 50)
            logging.info('Run: genRotamers_rdkit(inMol2=%s, outMol2=%s, debug=%s)\n' % (inMol2, outMol2, debug))

        # delete the exist mol2
        try:
            os.remove(outMol2)
        except:
            pass

        # command
        cmd = '%s -imol2 %s -omol2 %s -N %d genRotamers' % (self.rdkitrotamer, inMol2, outMol2, int(self.NRotamers))
        if debug:
            logging.info('Running: %s\n' % cmd)

        # generate rotamers
        Info = []
        rotcmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # grab output and error
        roterr, rotout = rotcmd.communicate()
        Info.append(rotout)
        logging.info(list(set(Info))[0])


    def optmizeRotamers(self, inMol2, outPDB, outEn, debug=True):
        '''

        :param inMol2:
        :param outPDB: obminimize outputs in PDB format defaultly and could not be changed!
        :return:
        '''
        if debug:
            logging.info('-' * 50)
            logging.info('Run: optmizeRotamers(inMol2=%s, outPDB=%s, outEn=%s, debug=%s)\n' % (inMol2, outPDB, outEn, debug))

        # delete the exist pdb
        try:
            os.remove(outPDB)
        except:
            pass

        # command
        cmd = '%s -ff %s -n %d -%s %s > %s' % (self.obminimize, self.Forcefield, self.NStep, self.Opt, inMol2, outPDB)
        if debug:
            logging.info('Running: %s\n' % cmd)

        # optimize
        optcmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # grab output and error
        optout, opterr = optcmd.communicate()

        # extract the energy
        optOutput = opterr.split('\n')

        index_list = []
        counter = 0
        for i in optOutput:
            if i.startswith('Time:'):
                index_list.append(counter-1)
            counter += 1
        En_list = [optOutput[i].split()[1] for i in index_list]

        # save the energy list
        #with open(outEn, 'w') as fout:
        #    fout.writelines('\n'.join(En_list))
        fout = open(outEn, 'w')
        i = 0
        for e in En_list:
            fout.write('%s, %d\n' % (str(e), i))
            i += 1
        fout.close()

        return En_list

    def calcRMS(self, optedPDB, outRMS, debug=True):
        tclFile = '%d.tcl' % random.randint(1, 10000)

        if debug:
            logging.info('-' * 50)
            logging.info('Run: calcRMS(optedPDB=%s, outRMS=%s, debug=%s)\n' % (optedPDB, outRMS, debug))

        fout = open(tclFile, 'w')

        outString = '''set outfile [open %s w]
    mol new %s waitfor all

    set Nframes [molinfo top get numframes]

    for {set i 0} { $i <= $Nframes} { incr i} {
        set mol0 [atomselect top "all" frame 0]
        set moli [atomselect top "all" frame $i]
        $moli move [measure fit $moli $mol0]
        puts $outfile "$i [measure rmsd $moli $mol0]"
    }
    exit

    ''' % (outRMS, optedPDB)

        # save to tcl
        fout.write(outString)
        fout.close()

        # calc rmsd
        rmsd_cmd = "%s -dispdev text -e %s > /dev/null" % (self.vmd, tclFile)

        if debug:
            logging.info('Running: %s\n' % rmsd_cmd)
        all_rmsd = subprocess.Popen(rmsd_cmd, shell=True).wait()

        # delete the tcl
        os.remove(tclFile)

        # return
        fcon = open(outRMS).readlines()
        return [float(i.strip().split()[1]) for i in fcon[:-1]]

    def plotCluster(self, enFile, rmsFile, figFile, outCsv, eps=0.01, minSamples=1, debug=True):
        if debug:
            logging.info('-' * 50)
            logging.info('Run: plotCluster(enFile=%s, rmsFile=%s, figFile=%s, outCsv=%s, eps=%s, minSamples=%s, debug=%s)\n'
                         % (enFile, rmsFile, figFile, outCsv, str(eps), str(minSamples), debug))

        # read the results
        Ens = np.array([float(i.strip().split(',')[0]) for i in open(enFile).readlines()])
        Frame = np.array([int(i.strip().split(',')[1]) for i in open(enFile).readlines()])

        Rms = np.array([float(i.strip().split()[1]) for i in open(rmsFile).readlines()[:-1]])
        #Frame = np.array([int(i.strip().split()[0]) for i in open(rmsFile).readlines()[:-1]])

        # gen the X matrix
        X = np.array(zip((Rms - min(Rms))/(max(Rms)-min(Rms)), (Ens - min(Ens))/(max(Ens)-min(Ens))))

        # Compute DBSCAN
        db = DBSCAN(eps=eps, min_samples=minSamples).fit(X)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

        # init the figure
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = 'k'

            class_member_mask = (labels == k)

            xy = X[class_member_mask & core_samples_mask]
            ax.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~core_samples_mask]
            ax.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=6)

        ax.set_title('Estimated number of clusters: %d' % n_clusters_)
        ax.set_xlabel('RMS (normalized)')
        ax.set_ylabel('Energy (normalized)')
        fig.savefig(figFile)
        # plt.show()

        logging.info('Estimated number of clusters: %d' % n_clusters_)

        # prepare output csv
        df = pd.DataFrame(zip(Frame, Ens, Rms, labels), columns=['Frame', 'En', 'RMS', 'Cluster'])
        df.to_csv(outCsv)

        return df

    def pickPDBStructure(self, Nthstr, pdbFile, debug=True):
        '''
        :param Nthstr:  get the N th structure. Starts from 0
        :param pdbFile: pdb file that contains many pdb structures
        :return:
        '''
        if debug:
            logging.info('-' * 50)
            logging.info('Run: pickPDBStructure(Nthstr=%s, pdbFile=%s, debug=%s)\n' % (Nthstr, pdbFile, debug))

        # load all the pdb
        fcon = open(pdbFile).readlines()

        # build end_index
        end_index = [0]
        counter = 1
        for i in fcon:
            if i.startswith('END'):
                end_index.append(counter)
            counter += 1

        # get the Nth structure
        if Nthstr < 0 or Nthstr > len(end_index) - 1:
            logging.warn('Out of range! Trying to get the %dth structure from %d in total.' % (Nthstr, len(end_index)-1))
            return ''
        picked_str = fcon[end_index[Nthstr]:end_index[Nthstr+1]]

        return picked_str

    def uniqueClusters(self, inCsv, inPDB, outCsv, outPDB, debug=True):
        '''
        To find the lowest-energy structure from each cluster.
        :param inCsv:
        :param inPDB:
        :param outCsv:
        :param outPDB:
        :return:
        '''
        if debug:
            logging.info('-' * 50)
            logging.info('Run: uniqueClusters(inCsv=%s, inPDB=%s, outCsv=%s, outPDB=%s, debug=%s)\n'
                         % (inCsv, inPDB, outCsv, outPDB, debug))

        # read the csv info
        df_in = pd.DataFrame.from_csv(inCsv)
        # read the pdb
        pdb_in = open(inPDB).readlines()

        # pick conformation
        df = df_in.sort_values(by=['Cluster', 'En'])
        df.drop_duplicates('Cluster', keep='first', inplace=True)
        df['Frame_old'] = df['Frame']
        df.sort_values(by=['En'], inplace=True)
        df['Frame'] = range(len(df))

        # save csv
        df.to_csv(outCsv)

        # pick pdb
        outPDB_list = []
        for i in df['Frame_old']:
            i_str = self.pickPDBStructure(i, inPDB, debug=False)
            outPDB_list += i_str

        # save pdb
        open(outPDB, 'w').writelines(outPDB_list)

    def splitePDBtoXYZ(self, pdbFile, outDir, outPrefix, molName, debug=True):
        '''
        to splite structures in the PDB file into seperate xyz files
        :param pdbFile:
        :param outDir:
        :param debug:
        :return:
        '''

        if debug:
            logging.info('-' * 50)
            logging.info('Run: splitePDBtoXYZ(pdbFile=%s, outDir=%s, outPrefix=%s, molName=%s, debug=%s)\n'
                         % (pdbFile, outDir, outPrefix, molName, debug))

        if not os.path.exists(outDir):
            try:
                os.makedirs(outDir)
            except:
                pass
        else:
            try:
                shutil.rmtree(outDir)
                os.makedirs(outDir)
            except:
                pass


        # read pdb
        fcon = open(pdbFile).readlines()

        # build end_index
        end_index = [0]
        counter = 1
        for i in fcon:
            if i.startswith('END'):
                end_index.append(counter)
            counter += 1

        if debug:
            logging.info('%d structures were found from %s' % (len(end_index)-1, pdbFile))

        Nthstr = 0
        while Nthstr < len(end_index)-1:
            # get the Nth structure
            picked_str = fcon[end_index[Nthstr]:end_index[Nthstr + 1]]

            # save pdb
            open('%s/%d.pdb' % (outDir, Nthstr), 'w').writelines(picked_str)

            # convert pdb to xyz
            cmd = '%s -ipdb %s/%d.pdb -O %s/%s%d_%s.xyz' % (self.obabel, outDir, Nthstr, outDir, outPrefix, Nthstr, molName)
            cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = cmd.communicate()

            # delete pdb
            os.remove('%s/%d.pdb' % (outDir, Nthstr))

            Nthstr += 1



    def samplingAll(self, molXYZ, debug=True):
        if debug:
            logging.info('-' * 50)
            logging.info('Run: samplingAll(molXYZ=%s, debug=%s)\n'
                         % (molXYZ, debug))

        # get mol name
        mol = molXYZ.split('.xyz')[0]

        # mkdir
        try:
            os.makedirs('%s/xyz/' % mol)
        except:
            pass

        # logfile
        logFile = '%s/csearch.log' % mol
        logging.basicConfig(filename=logFile, filemode='w', level=logging.INFO)

        info_text = '''%s
        mol = %s

        NRotamers = %d
        ForceField = %s
        NStep = %d
        Opt = %s
        eps = %s
        minSamples = %d
        outPrefix = %s

        obabel = %s
        obrotamer = %s
        obminimize = %s
        ''' % ("-"*50, molXYZ, self.NRotamers, self.Forcefield, self.NStep, self.Opt, str(self.eps), self.minSamples,
               self.outPrefix, self.obabel, self.rdkitrotamer, self.obminimize)
        logging.info(info_text)
        print info_text

        # convert xyz to mol2
        cmd = '%s -ixyz %s.xyz -O %s/%s.mol2' % (self.obabel, molXYZ, mol, mol)
        if debug:
            logging.info('Running: %s' % cmd)

        # convert
        convcmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # grab output and error
        convout, converr = convcmd.communicate()

        # set the parameters
        inMol2 = '%s/%s.mol2' % (mol, mol)
        rotamers = '%s/%s.rot.mol2' % (mol, mol)

        opted = '%s/%s.opted.pdb' % (mol, mol)
        optedEN = '%s/%s.opted.en' % (mol, mol)
        optedRMS = '%s/%s.opted.rms' % (mol, mol)

        clusterFig = '%s/%s.cluster.png' % (mol, mol)
        clusterCsv = '%s/%s.cluster.csv' % (mol, mol)

        uniqueCsv = '%s/%s.unique.csv' % (mol, mol)
        uniquePDB = '%s/%s.unique.pdb' % (mol, mol)

        # perform calculations
        #self.genRotamers(inMol2, rotamers, debug)
        self.genRotamers_rdkit(inMol2, rotamers, debug)
        self.optmizeRotamers(rotamers, opted, optedEN, debug)
        self.calcRMS(opted, optedRMS, debug)
        self.plotCluster(optedEN, optedRMS, clusterFig, clusterCsv, eps=self.eps, minSamples=self.minSamples, debug=debug)
        self.uniqueClusters(clusterCsv, opted, uniqueCsv, uniquePDB, debug)
        self.splitePDBtoXYZ(uniquePDB, '%s/xyz/' % mol, self.outPrefix, mol, debug)



if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser(
        description='Perform conformation search by randomly assign the dihedral angle of single bonds.')
    parser.add_argument("--NRotamers", nargs='?', type=int, default=1000, help="Number of rotamers to generate")
    parser.add_argument("--Forcefield", nargs='?', type=str, default="UFF", help="Force filed to use")
    parser.add_argument("--NStep", nargs='?', type=int, default=2500, help="Max minimization steps for each rotamer")
    parser.add_argument("--eps", nargs='?', type=float, default=0.01, help="eps value used by DBScan")
    parser.add_argument("--minSamples", nargs='?', type=int, default=1, help="Minimum samples allow for a cluster")
    parser.add_argument("--outPrefix", nargs='?', type=str, default="CSearch_", help="Prefix used for output xyz")
    parser.add_argument("--debug", nargs='?', type=str, default="False", help="Debug. Default: False")

    parser.add_argument("reclustering", nargs='?', help="Perform reclustering or not")
    parser.add_argument("mol", type=str, default="", help="Input the molecule file (with file type e.g. 'mol.xyz')")

    # all arguments
    args = parser.parse_args()

    CS = CSearchRand()

    #mol = 'CH3CHSCOO-2'
    mol = args.mol[:-4]
    moltype = args.mol[-3:]

    if moltype not in ['xyz']:
        if moltype in ['smi']:
            cmd = '%s -i%s %s.%s -O %s.xyz --gen3D' % (CS.obabel, moltype, mol, moltype, mol)
        else:
            # convert .pdb to .xyz
            cmd = '%s -i%s %s.%s -O %s.xyz' % (CS.obabel, moltype, mol, moltype, mol)
        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = cmd.communicate()

    # reclustering or new sampling
    if not args.reclustering:
        print 'new sampling'

        startTime = time.time()

        CS = CSearchRand()
        CS.debug = args.debug  # False

        # for minimization
        CS.NRotamers = args.NRotamers  # Default 1000    # Number of rotamers to generate
        CS.Forcefield = args.Forcefield  # Default 'UFF'  # force filed to use
        CS.NStep = args.NStep  # Default 2500        # max minimization steps for each rotamer

        # for DBScan clustering
        CS.eps = args.eps  # Default 0.01          # eps value used by DBScan
        CS.minSamples = args.minSamples  # Default 1      # minimum samples allow for a cluster

        CS.outPrefix = args.outPrefix  # Default '_l_Xe_r_'

        CS.samplingAll(mol, debug=CS.debug)

        endTime = time.time()
        logging.info('Time: %s min' % ((endTime - startTime) / 60))
        print 'Time: %s min' % round((endTime - startTime) / 60, 2)

        exit()
    else:
        print 'reclustering with {eps: %s, minSamples: %s}\n' % (str(args.eps), str(args.minSamples))

        startTime = time.time()

        # output the logging info to the stdout
        logging.basicConfig(level=logging.INFO)

        # starts from mol2!!!
        inMol2 = '%s.mol2' % mol

        rotamers = '%s/%s.rot.mol2' % (mol, mol)
        opted = '%s/%s.opted.pdb' % (mol, mol)
        optedEN = '%s/%s.opted.en' % (mol, mol)
        rmsTCL = '%s/%s.rms.tcl' % (mol, mol)
        optedRMS = '%s/%s.opted.rms' % (mol, mol)

        clusterFig = '%s/%s.cluster.png' % (mol, mol)
        clusterCsv = '%s/%s.cluster.csv' % (mol, mol)

        uniqueCsv = '%s/%s.unique.csv' % (mol, mol)
        uniquePDB = '%s/%s.unique.pdb' % (mol, mol)

        # outPrefix = 'Xe'

        Csearcher = CSearchRand()
        Csearcher.outPrefix = args.outPrefix
        # Csearcher.NRotamers = 100
        # Csearcher.genRotamers(inMol2, rotamers)
        # Csearcher.genRotamers_rdkit(inMol2, rotamers)
        # Csearcher.optmizeRotamers(rotamers, opted, optedEN)
        # Csearcher.calcRMS(opted, optedRMS, debug=True)
        Csearcher.plotCluster(optedEN, optedRMS, clusterFig, clusterCsv, eps=args.eps, minSamples=args.minSamples)
        Csearcher.uniqueClusters(clusterCsv, opted, uniqueCsv, uniquePDB)
        Csearcher.splitePDBtoXYZ(uniquePDB, '%s/xyz/' % mol, Csearcher.outPrefix, mol)

        endTime = time.time()
        logging.info('Time: %s min' % (round((endTime - startTime) / 60, 2)))

        exit()


    '''
    #### step by step version
    #mol = 'Hg_l_CH3CHSCOO_r_2-2'
    #mol = 'CH3CHSCOO-2'
    #mol = 'SCHCH2COO2-3'

    mol = args.mol

    startTime = time.time()

    # output the logging info to the stdout
    logging.basicConfig(level=logging.INFO)

    # starts from mol2!!!
    inMol2 = '%s.mol2' % mol

    rotamers = '%s/%s.rot.mol2' % (mol, mol)
    opted = '%s/%s.opted.pdb' % (mol, mol)
    optedEN = '%s/%s.opted.en' % (mol, mol)
    rmsTCL = '%s/%s.rms.tcl' % (mol, mol)
    optedRMS = '%s/%s.opted.rms' % (mol, mol)

    clusterFig = '%s/%s.cluster.png' % (mol, mol)
    clusterCsv = '%s/%s.cluster.csv' % (mol, mol)

    uniqueCsv = '%s/%s.unique.csv' % (mol, mol)
    uniquePDB = '%s/%s.unique.pdb' % (mol, mol)

    #outPrefix = 'Xe'

    Csearcher = CSearchRand()
    #Csearcher.NRotamers = 100
    #Csearcher.genRotamers(inMol2, rotamers)
    #Csearcher.genRotamers_rdkit(inMol2, rotamers)
    #Csearcher.optmizeRotamers(rotamers, opted, optedEN)
    #Csearcher.calcRMS(opted, optedRMS, debug=True)
    Csearcher.plotCluster(optedEN, optedRMS, clusterFig, clusterCsv, eps=0.1, minSamples=1)
    Csearcher.uniqueClusters(clusterCsv, opted, uniqueCsv, uniquePDB)
    Csearcher.splitePDBtoXYZ(uniquePDB, '%s/xyz/' % mol, Csearcher.outPrefix, mol)

    endTime = time.time()
    logging.info('Time: %s min' % ((endTime-startTime)/60))
    '''
