#!/home/p6n/anaconda2/bin/python
#!/usr/bin/python
from __future__ import print_function
import argparse
import subprocess, os, csv, shutil, re, sys, getopt, tarfile, logging
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt


class ReplicaFlow:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        try:
            self.hostname = os.uname()[1].split('-')[1]
        except:
            self.hostname = ''
        if self.hostname in ['condo']:
            self.MDHomeDir = "/home/p6n/tools/NAMD_2.11_Linux-x86_64-netlrts/"
        else:
            self.MDHomeDir = "/home/p6n/tools/NAMD_2.12_Linux-x86_64-netlrts/"
            self.antechamber = '/home/p6n/tools/amber14/bin//antechamber'
            self.obabel = '/home/p6n/anaconda2/bin/obabel'
            self.vmd = '/home/p6n/tools/vmd-1.9.2/bin/vmd'
            #self.gnuplot = '/usr/bin/gnuplot'
            os.environ.update({'AMBERHOME':'/home/p6n/tools/amber14/'})

    #converts SMILES string to 3D structure .mol2 output
    def call_babel(self, file_type, input, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: call_babel(file_type=%s, input=%s, debug=%s)' % (file_type, input, debug))
            logging.info('Reading file or SMILES: %s' % input)

        # prepare command
        if file_type in ['SMILES', 'smi'] and not os.path.exists(input):
            command_line = '%s -:"%s" -O mol.pdb --gen3d --conformer --systematic --ff GAFF' % (self.obabel, input)
        elif os.path.exists(input):
            command_line = '%s -i%s %s -O mol.pdb' % (self.obabel, file_type, input)
        else:
            logging.info('Cannot find %s file %s. Check input!' % (file_type, input))
            return

        if debug:
            logging.info('Running: %s' % command_line)
            logging.info('Generate file: mol.pdb\n')

        # run the command
        babelcmd=subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # grab output and error
        babelout, babelerr = babelcmd.communicate()

        # check the babel error
        if not re.match(r'^1 ', babelerr):
            logging.ERROR("Error with SMILES String: %s" % babelerr)
            return

    #fixes pdb from call_babel
    def fix_pdb(self, inFile='mol.pdb', outFile='mol_fix.pdb', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: fix_pdb(inFile=%s, outFile=%s, debug=%s)' % (inFile, outFile, debug))

        file_in = open(inFile, 'r')
        file_out = open(outFile, 'w')
        charge=0
        for line in file_in:
            temp = line.split()
            if (temp[0]== 'HETATM' or temp[0]=='ATOM'):
                temp[0]='ATOM'
                temp[2]=temp[2][0]
                temp[3]='UNK'
                if (len(temp))==11:
                    temp.extend(['0'])
                    temp[11]=temp[10]
                    temp[10]=temp[9]
                    temp[9]=temp[8]
                    temp[8]=temp[7]
                    temp[7]=temp[6]
                    temp[6]=temp[5]

                temp[5]='0'
                file_out.write('{0:>4}  {1:>5}  {2:<4}{3:>3} {4:>1}{5:>4}      {6:>6}{7:>8}{8:>8}{9:>6}{10:>6}      {11:>2}{12:>1}\n'.format(temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],
                        temp[7],temp[8],temp[9],temp[10],temp[11][0], temp[11][1:]))
                charge=charge+temp[11].count('+')
                charge=charge-temp[11].count('-')
            else:
                file_out.write(line)
        file_out.close()
        file_in.close()
        return charge

    #generates charmm readable files
    def call_antechamber(self, netcharge, inFile='mol_fix.pdb', outFile='molnew.pdb', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: call_antechamber(netcharge=%s, inFile=%s, outFile=%s, debug=%s)' % (str(netcharge), inFile, outFile, debug))

        #find_amber = subprocess.Popen("which antechamber", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #antechmbr, err = find_amber.communicate()

        #antecmd = antechmbr.strip() + " -fi pdb -i mol_fix.pdb -fo charmm -o mol -c bcc -nc " + str(netcharge)
        antecmd = '%s -fi pdb -i %s -fo charmm -o mol -c bcc -nc %s' % (self.antechamber, inFile, str(netcharge))
        if debug:
            logging.info('Running: %s' % antecmd)
        ante = subprocess.Popen(antecmd, shell=True).wait()

        #ant_pdbcmd = antechmbr.strip() + " -fi pdb -i mol_fix.pdb -fo pdb -o molnew.pdb -rn MOL " + str(netcharge)
        ant_pdbcmd = '%s -fi pdb -i %s -fo pdb -o %s -rn MOL %s' % (self.antechamber, inFile, outFile, str(netcharge))
        if debug:
            logging.info('Running: %s\n' % ant_pdbcmd)
        ant_pdb = subprocess.Popen(ant_pdbcmd, shell=True).wait()

    #modifies prm to add LJ potential to hydrogens lacking it
    def fix_prm(self, inFile='mol.prm', outFile='mol_fix.prm', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: fix_prm(inFile=%s, outFile=%s, debug=%s)\n' % (inFile, outFile, debug))

        file_in = open(inFile, 'r')
        file_out = open(outFile, 'w')

        for line in file_in:
            temp = line.split()
            if (len(temp) == 7) and (temp[2] == '-0.0000'):
                temp[2] = '-0.0157'
                temp[3] = '1.3870'
                temp[5] = '-0.0078'
                temp[6] = '1.3870'
                file_out.write('{0:>2}      {1:>4}   {2:>7}    {3:>6}      {4:>4}   {5:>7}    {6:>6}\n'
                               .format(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6]))

            else:
                file_out.write(line)
        file_in.close()
        file_out.close()

        # update the mol.prm file
        shutil.copy("mol_fix.prm", "mol.prm")
        os.remove("mol_fix.prm")




    #calls vmd's psfgen to generate psf and pdb files
    def call_psfgen(self, outFile='mol_psfgen.pgn', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: call_psfgen(outFile=%s, debug=%s)' % (outFile, debug))

        file_out = open(outFile, 'w')

        outString = '''package require psfgen
    package require autoionize
    topology mol.inp
    topology mol.rtf
    segment MOL {pdb molnew.pdb}
    coordpdb molnew.pdb MOL
    guesscord
    writepdb mol.pdb
    writepsf mol.psf
    autoionize -psf mol.psf -pdb mol.pdb -neutralize -o mol
    quit vmd
    '''
        file_out.write(outString)
        file_out.close()

        psf_cmds = "%s -dispdev text -eofexit < %s > temp.out 2> temp-error.out" % (self.vmd, outFile)

        if debug:
            logging.info('The config file for psfgen is %s: \n\n%s' % (outFile, outString))
            logging.info('Running: %s' % psf_cmds)

        psf = subprocess.Popen(psf_cmds, shell=True).wait()


    #calls VMD to add solvation box
    def solvate_cmds(self, outFile='mol_solvate.tcl', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: solvate_cmds(outFile=%s, debug=%s)' % (outFile, debug))

        file_out = open(outFile, 'w')

        outString = '''package require solvate
    solvate mol.psf mol.pdb -t 10 -o mol_wb
    quit vmd

        '''

        file_out.write(outString)
        file_out.close()

        solv_cmds = "%s -dispdev text -eofexit < %s > temp.out 2> temp-error.out" % (self.vmd, outFile)

        if debug:
            logging.info('The config file for solvation is %s: \n\n%s' % (outFile, outString))
            logging.info('Running: %s' % solv_cmds)

        solv = subprocess.Popen(solv_cmds, shell=True).wait()

    #makes xsc file for namd
    def make_xsc(self, inFile='mol_wb.pdb', outFile='mol.xsc', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: make_xsc(inFile=%s, outFile=%s, debug=%s)' % (inFile, outFile, debug))

        file_in = open(inFile, 'r')
        file_out = open(outFile, 'w')

        for line in file_in:
            if line.startswith("CRYST1"):
                size = line[9:15]

        file_out.write("#NAMD extended system configuration restart file\n")
        file_out.write("#$LABELS step a_x a_y a_z b_x b_y b_z c_x c_y c_z o_x o_y o_z s_x s_y s_z s_u s_v s_w\n")
        file_out.write("0 " + size + " 0 0 0 " + size + " 0 0 0 " + size + " 0 0 0 0 0 0 0 0 0)")
        file_in.close()
        file_out.close()

    #edit pdb to restrain center of mass
    def rest_vmd(self, outFile='mol_rest.tcl', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: rest_vmd(outFile=%s, debug=%s)' % (outFile, debug))

        file_out = open(outFile, 'w')

        outString = '''mol addfile mol_wb.pdb
    set selall [atomselect top "all"]
    set selsolute [atomselect top "segid MOL"]
    $selall set occupancy 0.0
    $selsolute set occupancy 1.0
    $selall writepdb molref.pdb
    quit vmd

    '''

        file_out.write(outString)
        file_out.close()

        rest_cmds = "%s -dispdev text -eofexit < %s > temp.out 2> temp-error.out" % (self.vmd, outFile)

        if debug:
            logging.info('The config file for rest_vmd is %s: \n\n%s' % (outFile, outString))
            logging.info('Running: %s' % rest_cmds)

        rest = subprocess.Popen(rest_cmds, shell=True).wait()

    #creats colvar to restrain center of mass
    def rest_colvars(self, outFile='colvars.tcl', debug=True):
        file_out = open(outFile, 'w')

        outString = '''colvar {
        name molcom
        distance {
            group1 {
                atomsFile molref.pdb
                atomsCol O
                atomsColValue 1.0
            }

            group2 {
                dummyAtom (0.000, 0.000, 0.000)
            }
        }
    }

    harmonic {
        name molrestcom
        colvars molcom
        centers 0.0
        forceConstant 5.0
    }

    '''

        file_out.write(outString)
        file_out.close()

        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: rest_colvars(outFile=%s, debug=%s)' % (outFile, debug))
            logging.info('The config file for rest_colvars is %s: \n\n%s' % (outFile, outString))

    #calls namd for reg
    ##mpirun location may change depending on system##
    def call_namd_exp(self, option, num_processors, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: call_namd_exp(option=%s, num_processors=%s, debug=%s)' %
                         (option, str(num_processors), debug))

        # NVT run
        if self.hostname in ['condo']:
            namd_cmds = "%s/charmrun ++local +p%s %s/namd2 mol%s-nvt.namd > mol%s-nvt.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        else:
            namd_cmds = "%s/charmrun +p%s %s/namd2 mol%s-nvt.namd > mol%s-nvt.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        if debug:
            logging.info('Running: %s' % namd_cmds)
        namd=subprocess.Popen(namd_cmds, shell=True).wait()

        # NPT run
        if self.hostname in ['condo']:
            namd_cmds = "%s/charmrun ++local +p%s %s/namd2 mol%s-npt.namd > mol%s-npt.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        else:
            namd_cmds = "%s/charmrun +p%s %s/namd2 mol%s-npt.namd > mol%s-npt.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        if debug:
            logging.info('Running: %s' % namd_cmds)
        namd=subprocess.Popen(namd_cmds, shell=True).wait()

    #calls namd for gbis, and gas
    def call_namd(self, option, num_processors, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: call_namd(option=%s, num_processors=%s, debug=%s)' %
                         (option, str(num_processors), debug))
        if self.hostname in ['condo']:
            namd_cmds = "%s/charmrun ++local +p%s %s/namd2 mol%s.namd > mol%s.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        else:
            namd_cmds = "%s/charmrun +p%s %s/namd2 mol%s.namd > mol%s.out" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, option, option)
        if debug:
            logging.info('Running: %s' % namd_cmds)

        namd=subprocess.Popen(namd_cmds, shell=True).wait()

    #performs REMD using user input for number of replicas and number of runs, output folder dynamically generated
    def namd_remd(self, option, file_extension, pdb_extension, num_processors, num_reps=24, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: namd_remd(option=%s, file_extension=%s, pdb_extension=%s, num_processors=%s, num_reps=%s, debug=%s)'
                  % (option, file_extension, pdb_extension, str(num_processors), str(num_reps), debug))

        #num_reps = "24"
        #num_reps = num_processors
        num_runs = "1000"

        outFile_job = 'job%s.conf' % option
        outFile_conf = 'mol_rep%s.conf' % option

        folder_out = 'output%s' % option

        if os.path.exists(folder_out):
            shutil.rmtree(folder_out)
        os.mkdir(folder_out)
        for i in range(int(num_reps)):
            os.mkdir(folder_out+'/%d' % i)

        job_out = open(outFile_job, 'w')

        outString_job = '''source mol_rep%s.conf
    #prevents VMD from reading replica.namd by trying command only NAMD has
    if {! [catch numPes]} {source replica.namd}

    ''' % (option)

        job_out.write(outString_job)
        job_out.close()


        conf_out = open(outFile_conf, 'w')

        outString_conf = '''    set num_replicas %s
    set min_temp 298
    set max_temp 398
    set steps_per_run 1000
    set num_runs %s
    # num_runs should be divisible by runs_per_frame * frames_per_restart

    set runs_per_frame 1
    set frames_per_restart 1
    set namd_config_file "mol_rep%s.namd"
    set output_root "%s/%%s/mol";

    # the following used only by show_replicas.vmd
    set psf_file "mol%s.psf"
    set pdb_file "mol%s.pdb"
    set initial_pdb_file "mol%s.pdb"
    set fit_pdb_file "mol%s.pdb"


    ''' % (str(num_reps), str(num_runs), option, folder_out, file_extension, pdb_extension, pdb_extension, pdb_extension)

        conf_out.write(outString_conf)
        conf_out.close()

        if self.hostname in ['condo']:
            remd_cmds = "%s/charmrun ++local +p%s %s/namd2 +replicas %s job%s.conf +stdout %s/%%d/job0.%%d.log > job%s.out 2>&1" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, str(num_reps), option, folder_out, option)
        else:
            remd_cmds = "%s/charmrun +p%s %s/namd2 +replicas %s job%s.conf +stdout %s/%%d/job0.%%d.log > job%s.out 2>&1" % \
                        (self.MDHomeDir, str(num_processors), self.MDHomeDir, str(num_reps), option, folder_out, option)
        if debug:
            logging.info('The job file for namd_remd is %s: \n\n%s' % (outFile_job, outString_job))
            logging.info('The config file for namd_remd is %s: \n\n%s' % (outFile_conf, outString_conf))
            logging.info('Running: %s' % remd_cmds)
        remd = subprocess.Popen(remd_cmds, shell=True).wait()

    #sorts replicas
    def sort_replicas(self, option, num_reps=24, debug=True):
        sort_reps_cmds = "%s/sortreplicas output%s/%%d/mol.job0 %s 1" % (self.MDHomeDir, option, str(num_reps))
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: sort_replicas(option=%s, num_reps=%s, debug=%s)' % (option, str(num_reps), debug))
            logging.info('Running: %s' % sort_reps_cmds)
        sort_reps = subprocess.Popen(sort_reps_cmds, shell=True).wait()

    #measures clusters then creates pdb and files for clusters from lowest temp replica
    def vmd_cluster(self, option, num_clusters=5, cutoff=1.0, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: vmd_cluster(option=%s, num_clusters=%s, cutoff=%s, debug=%s)' % (option, str(num_clusters), str(cutoff), debug))

        # make cluster dir
        clust_out = 'clusters%s' % option
        if os.path.exists(clust_out):
            shutil.rmtree(clust_out)
        os.mkdir(clust_out)

        # prepare the mol_cluster.tcl (cluster analysis on lowest 3 temperature replicas)
        sed_cmds = 'sed -i "s/NCLUSTERS/%s/g" mol_cluster%s.tcl' % (str(num_clusters), option)
        sedp = subprocess.Popen(sed_cmds, shell=True).wait()
        sed_cmds = 'sed -i "s/CUTOFF/%s/g" mol_cluster%s.tcl' % (str(cutoff), option)
        sedp = subprocess.Popen(sed_cmds, shell=True).wait()

        clust_cmds = "%s -dispdev text -e mol_cluster%s.tcl > mol_cluster%s.log" % (self.vmd, option, option)

        if debug:
            logging.info('Running: %s' % sed_cmds)
            logging.info('Running: %s' % clust_cmds)

        clust = subprocess.Popen(clust_cmds, shell=True).wait()

        # make conf dir
        conf_out = 'conf%s' % option
        if os.path.exists(conf_out):
            shutil.rmtree(conf_out)
        os.mkdir(conf_out)

        # gene conf file
        outFile_conf = 'mol_conf%s.tcl' % option
        conf_file = open(outFile_conf, 'w')
        outString_conf = '''#creates pdb files for the clusters from the 1st replica
    for {set i 0} {$i < %d} {incr i} {
        set dcd "clusters%s/cluster0.$i.dcd"
        set psf "mol.psf"
        mol load psf $psf dcd $dcd
        set selconf [atomselect top "all"]
        $selconf writepdb conf%s/cluster0.$i.pdb
    }
    exit
    ''' % (int(num_clusters), option, option)

        conf_file.write(outString_conf)
        conf_file.close()

        # run vmd with conf file
        conf_cmds = "%s -dispdev text -e mol_conf%s.tcl > conf.log" % (self.vmd, option)
        if debug:
            logging.info('The conf file for vmd_cluster is %s: \n\n%s' % (outFile_conf, outString_conf))
            logging.info('Running: %s' % conf_cmds)
        conf = subprocess.Popen(conf_cmds, shell=True).wait()


        # convert pdb into xyz for displaying
        for pdb in os.listdir(conf_out):
            fname = pdb[:-4]
            command_line = '%s -ipdb %s/%s.pdb -O %s/%s.xyz' % (self.obabel, conf_out, fname, conf_out, fname)
            try:
                subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
            except:
                logging.WARN('Faild to convert pdb file %s to xyz format.' % fname)


        # plot the rmsd of the three trajectories with lowest temperature
        rmsd_dat = 'mol_rmsdtt%s.dat' % option
        outFig_rmsd = 'mol_rmsdtt%s.png' % option
        try:
            df = pd.read_csv(rmsd_dat, sep='\s+')

            # init the figure
            fig = plt.figure()
            ax = fig.add_subplot(111)

            ax.plot(df.frame, df.mol0, 'b-', label='Replica One')
            ax.plot(df.frame, df.mol1, 'r-', label='Replica Two')
            ax.plot(df.frame, df.mol2, 'g-', label='Replica Three')
            ax.legend(loc='lower right')

            #ax.set_title('RMSD Trajectory')
            ax.set_xlabel('Frame')
            ax.set_ylabel('RMSD (Angstrom)')
            fig.savefig(outFig_rmsd)
        except:
            logging.WARN('Failed to plot the rmsd of the trajectories. File: %s' % str(outFig_rmsd))

    #determines RMSD of explict versus gas and gbis
    def calc_rmsd(self, outFile='mol_rmsd_all.tcl', outData='mol_rmsd_all.dat', debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: calc_rmsd(outFile=%s, outData=%s, debug=%s)' % (outFile, outData, debug))

        all_rmsd_in = open(outFile, 'w')

        outString = '''set outfile [open %s w]
    mol new conf/cluster0.0.pdb
    mol new conf_gas/cluster0.0.pdb
    mol new conf_gbis/cluster0.0.pdb

    for {set i 0} {$i <=2} {incr i} {
        set mol$i [atomselect $i "all"]
    }

    for {set j 1} {$j <=2} {incr j} {
        $mol0 move [measure fit $mol0 [set mol$j]]
        puts $outfile "RMSD:  [measure rmsd $mol0 [set mol$j]]"
    }
    exit

    ''' % outData

        # save to tcl
        all_rmsd_in.write(outString)
        all_rmsd_in.close()

        # calc rmsd
        all_rmsd_cmds = "%s -dispdev text -e %s > rmsd.out" % (self.vmd, outFile)
        if debug:
            logging.info('Running: %s' % all_rmsd_cmds)
        all_rmsd = subprocess.Popen(all_rmsd_cmds, shell=True).wait()

    #moves significant documents to output folder
    def collect_results(self, folder_name, gas=True, explicit=True, implicit=True, debug=True):
        if debug:
            logging.info('\n' + '-' * 50)
            logging.info('Run: collect_results(folder_name=%s, num_clusters=%s, debug=%s)' % (folder_name, num_clusters, debug))

        # prepare the results folder
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        os.makedirs(folder_name)

        if gas:
            subfolder = '%s/gas' % folder_name
            os.makedirs(subfolder)

            for f in ['mol.pdb', 'mol.psf', 'mol.prm', 'mol.rtf']:
                try:
                    shutil.copy(f, subfolder)
                except:
                    logging.info('Failed to copy %s to %s/' % (f, subfolder))

            try:
                shutil.copy("mol_cluster_gas.dat", "%s/mol_cluster.dat" % subfolder)
            except:
                logging.info('Failed to copy mol_cluster_gas.dat to %s/mol_cluster.dat' % subfolder)

            try:
                shutil.copy("mol_rmsdtt_gas.dat", "%s/mol_rmsdtt.dat" % subfolder)
            except:
                logging.info('Failed to copy mol_rmsdtt_gas.dat to %s/mol_rmsdtt.dat' % subfolder)

            try:
                shutil.copy("mol_rmsdtt_gas.png", "%s/mol_rmsdtt.png" % subfolder)
            except:
                logging.info('Failed to copy mol_rmsdtt_gas.png to %s/mol_rmsdtt.png' % subfolder)


            try:
                shutil.copytree("conf_gas/", "%s/configurations" % subfolder)
            except:
                logging.info('Failed to copy conf_gas/ to %s/configurations' % subfolder)

            try:
                shutil.copytree("clusters_gas/", "%s/clusters" % subfolder)
            except:
                logging.info('Failed to copy clusters_gas/ to %s/clusters' % subfolder)

            try:
                shutil.copytree("output_gas/", "%s/replicas" % subfolder)
            except:
                logging.info('Failed to copy output_gas/ to %s/replicas' % subfolder)

        if implicit:
            subfolder = '%s/gbis' % folder_name
            os.makedirs(subfolder)

            for f in ['mol.pdb', 'mol.psf', 'mol.prm', 'mol.rtf']:
                try:
                    shutil.copy(f, subfolder)
                except:
                    logging.info('Failed to copy %s to %s/' % (f, subfolder))

            try:
                shutil.copy("mol_cluster_gbis.dat", "%s/mol_cluster.dat" % subfolder)
            except:
                logging.info('Failed to copy mol_cluster_gbis.dat to %s/mol_cluster.dat' % subfolder)

            try:
                shutil.copy("mol_rmsdtt_gbis.dat", "%s/mol_rmsdtt.dat" % subfolder)
            except:
                logging.info('Failed to copy mol_rmsdtt_gbis.dat to %s/mol_rmsdtt.dat' % subfolder)

            try:
                shutil.copy("mol_rmsdtt_gbis.png", "%s/mol_rmsdtt.png" % subfolder)
            except:
                logging.info('Failed to copy mol_rmsdtt_gbis.png to %s/mol_rmsdtt.png' % subfolder)


            try:
                shutil.copytree("conf_gbis/", "%s/configurations" % subfolder)
            except:
                logging.info('Failed to copy conf_gbis/ to %s/configurations' % subfolder)

            try:
                shutil.copytree("clusters_gbis/", "%s/clusters" % subfolder)
            except:
                logging.info('Failed to copy clusters_gbis/ to %s/clusters' % subfolder)

            try:
                shutil.copytree("output_gbis/", "%s/replicas" % subfolder)
            except:
                logging.info('Failed to copy output_gbis/ to %s/replicas' % subfolder)

        if explicit:
            subfolder = '%s/wat' % folder_name
            os.makedirs(subfolder)

            for f in ['mol.pdb', 'mol.psf', 'mol.prm', 'mol.rtf', 'mol_wb.pdb', 'mol_wb.psf', 'mol_wb.prm',
                      'mol_cluster.dat', 'mol_rmsdtt.dat', 'mol_rmsdtt.png']:
                try:
                    shutil.copy(f, subfolder)
                except:
                    logging.info('Failed to copy %s to %s/' % (f, subfolder))

            try:
                shutil.copytree("conf/", "%s/configurations" % subfolder)
            except:
                logging.info('Failed to copy conf/ to %s/configurations' % subfolder)

            try:
                shutil.copytree("clusters/", "%s/clusters" % subfolder)
            except:
                logging.info('Failed to copy clusters/ to %s/clusters' % subfolder)

            try:
                shutil.copytree("output/", "%s/replicas" % subfolder)
            except:
                logging.info('Failed to copy output/ to %s/replicas' % subfolder)



    # sampling with explicit water model (regular operation as named before)
    def perform_explicit_wt_sampling(self, numprocs, num_reps, num_clusters, cutoff=1.0):
        reg_file_extension = "_wb"
        reg_option = ""
        reg_pdb_ext = "ref"

        # perform the nvt and npt running for explict water model
        self.call_namd_exp(reg_option, numprocs)
        # run the REMD simulation
        self.namd_remd(reg_option, reg_file_extension, reg_pdb_ext, numprocs, num_reps)
        self.sort_replicas(reg_option, num_reps)
        self.vmd_cluster(reg_option, num_clusters=num_clusters, cutoff=cutoff)

    # sampling with implicit water model using GBIS
    def perform_implicit_wt_sampling(self, numprocs, num_reps, num_clusters, cutoff=1.0):
        gbis_file_extension = ""
        gbis_option = "_gbis"
        gbis_pdb_ext = ""

        # prepare the system
        self.call_namd(gbis_option, numprocs)
        # run REMD simulation
        self.namd_remd(gbis_option, gbis_file_extension, gbis_pdb_ext, numprocs, num_reps)
        self.sort_replicas(gbis_option, num_reps)
        self.vmd_cluster(gbis_option, num_clusters=num_clusters, cutoff=cutoff)

    # sampling with in gas phase
    def perform_gas_phase_sampling(self, numprocs, num_reps, num_clusters, cutoff=1.0):
        gas_file_extension = ""
        gas_option = "_gas"
        gas_pdb_ext = ""

        # prepare the system
        self.call_namd(gas_option, numprocs)
        # run REMD simulation
        self.namd_remd(option=gas_option, file_extension=gas_file_extension, pdb_extension=gas_pdb_ext, num_processors=numprocs, num_reps=num_reps)
        self.sort_replicas(gas_option, num_reps)
        self.vmd_cluster(gas_option, num_clusters=num_clusters, cutoff=cutoff)


    def string_to_bool(self, s):
        if s.lower() in ['true', 'yes', '1']:
            return True
        else:
            return False

if __name__ == '__main__':
    # locate the file
    PATH_TO_BIN = os.path.dirname(os.path.realpath(__file__))
    #PATH_TO_LIB = '%s/lib' % os.path.dirname(PATH_TO_BIN)
    PATH_TO_LIB = '%s/lib' % PATH_TO_BIN

    debug = True
    rf = ReplicaFlow()

    # parse the arguments
    parser = argparse.ArgumentParser(
        description='Perform conformation search of small compound in explicit water, implicit water, and gas phase')
    parser.add_argument("-np", type=int, default=4,
                        help="Number of processors to allocate, should be N times of NR (Number of replicas)")
    parser.add_argument("-nr", type=int, default=4, help="Number of replicas to use")
    parser.add_argument("-nc", type=int, default=5, help="Number of clusters to generate")
    parser.add_argument("--cutoff", type=float, default=1.0, help="Threshold for clustering (Angstrom)")
    parser.add_argument("-t", type=str, default="smi", help="Type of the input file/string")
    parser.add_argument("--gas", type=str, default='False', help="Perform the claculation in gas phase")
    parser.add_argument("--explicit", type=str, default='False', help="Perform the claculation in explicit water environment")
    parser.add_argument("--implicit", type=str, default='False', help="Perform the claculation in implicit water environment")
    parser.add_argument("-o", type=str, default="csearch", help="Output directory")
    parser.add_argument("input", type=str, default="", help="Input SMILES string or path to the pdb file")

    # all arguments
    args = parser.parse_args()

    # check the args
    if args.np % args.nr != 0:
        logging.info('Number of processors to allocate, should be N times of NR (Number of replicas)')
        exit()
    elif args.input in ['']:
        logging.info('Cannot find the input string, please specify the input SMILES string or path to the pdb file.')

    else:
        # get the args paramenters
        outdir = args.o
        in_type = args.t
        instring = args.input
        num_procs = args.np
        num_reps = args.nr
        num_clusters = args.nc
        cutoff = args.cutoff

        gas = rf.string_to_bool(args.gas)
        explicit = rf.string_to_bool(args.explicit)
        implicit = rf.string_to_bool(args.implicit)

        logging.info('This script is running on %s' % rf.hostname)

        if gas == explicit == implicit == False:
            logging.info('Please provide at least one type of calculations. '
                         'Possible options are "--gas=True", "--explicit=True", and "--implicit=True".')
            exit()

        # check if outdir exist
        if os.path.exists(outdir):
            logging.info("Folder %s exists!" % outdir)
            exit()

        # prepare for all kinds of calculations
        # copy templates
        shutil.copytree("%s/templates" % PATH_TO_LIB, outdir)
        # copy the input xyz or pdb file to the output dir
        if in_type not in ['smi', 'SMI', 'SMILES']:
            if os.path.exists(instring):
                shutil.copy(instring, outdir)
        # change current work dir to outdir
        os.chdir(outdir)
        logging.info("Made directory! %s" % outdir)

        rf.call_babel(in_type, instring, debug)
        netcharge = rf.fix_pdb()
        rf.call_antechamber(netcharge)
        rf.fix_prm()
        rf.call_psfgen()
        rf.rest_colvars()

        rf.solvate_cmds()
        rf.make_xsc()
        rf.rest_vmd()

        # Explicit water REMD run (regular operations as named before)
        if explicit:
            rf.perform_explicit_wt_sampling(numprocs=num_procs, num_reps=num_reps, num_clusters=num_clusters, cutoff=cutoff)

        # Implicit water REMD run, GBIS operations
        if implicit:
            rf.perform_implicit_wt_sampling(numprocs=num_procs, num_reps=num_reps, num_clusters=num_clusters, cutoff=cutoff)

        # gas phase operations
        if gas:
            rf.perform_gas_phase_sampling(numprocs=num_procs, num_reps=num_reps, num_clusters=num_clusters, cutoff=cutoff)

        # copy the result from conf/ to output directory
        rf.collect_results("../%s_results" % outdir, gas=gas, explicit=explicit, implicit=implicit)

    logging.info("\nAll done!")

