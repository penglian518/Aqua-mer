import os, shutil, subprocess, logging
from .PhreeqcPrepare import PhreeqcPrepare
from .QMCalculationPrepare import QMCalculationPrepare, QMResultsCalculation
from django.core.mail import send_mail

class JobManagement:
    def __init__(self):
        self.DjangoHome = '/home/p6n/workplace/website/cyshg'
        self.obabel = '/home/p6n/anaconda2/bin/obabel'
        self.JobLocation = 'media'

    #### public functions ####
    def Convert2XYZ(self, obj, JobType='csearch'):
        # get basic info
        job_id = obj.JobID
        job_dir = '%s/media/%s/jobs/%s' % (self.DjangoHome, JobType, obj.JobID)

        mol_name = '%s-%d' % (JobType, job_id)

        try:
            os.makedirs(job_dir)
        except:
            pass
        if JobType in ['pka', 'logk']:
            if JobType in ['pka']:
                ligand_name = 'A'
                complex_name = 'HA'
            elif JobType in ['logk']:
                ligand_name = 'L'
                complex_name = 'ML'
                metal_name = 'M'

            if obj.UploadedFile:
                file_name = os.path.basename(obj.UploadedFile.path)
                file_type = obj.UploadedFileType

                uploaded_file = '%s/%s' % (job_dir, file_name)
                input_file = '%s/%s_%s.%s' % (job_dir, ligand_name, mol_name, file_type)
                # copy input file to input.file_type
                shutil.copy(uploaded_file, input_file)

                # convert smi to xyz file
                if file_type not in ['xyz']:
                    cmd = '%s -i%s %s -O %s/%s_%s.xyz' % (self.obabel, file_type, input_file, job_dir, ligand_name, mol_name)
                    cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, err = cmd.communicate()
            if obj.UploadedFileP1:
                file_name = os.path.basename(obj.UploadedFileP1.path)
                file_type = obj.UploadedFileTypeP1

                uploaded_file = '%s/%s' % (job_dir, file_name)
                input_file = '%s/%s_%s.%s' % (job_dir, complex_name, mol_name, file_type)
                # copy input file to input.file_type
                shutil.copy(uploaded_file, input_file)

                # convert smi to xyz file
                if file_type not in ['xyz']:
                    cmd = '%s -i%s %s -O %s/%s_%s.xyz' % (self.obabel, file_type, input_file, job_dir, complex_name, mol_name)
                    cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, err = cmd.communicate()
            if JobType in ['logk']:
                if obj.UploadedFileM:
                    file_name = os.path.basename(obj.UploadedFileM.path)
                    file_type = obj.UploadedFileTypeM

                    uploaded_file = '%s/%s' % (job_dir, file_name)
                    input_file = '%s/%s_%s.%s' % (job_dir, metal_name, mol_name, file_type)
                    # copy input file to input.file_type
                    shutil.copy(uploaded_file, input_file)

                    # convert smi to xyz file
                    if file_type not in ['xyz']:
                        cmd = '%s -i%s %s -O %s/%s_%s.xyz' % (self.obabel, file_type, input_file, job_dir, metal_name, mol_name)
                        cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        out, err = cmd.communicate()
            if obj.SmilesStr:
                file_type = 'smi'

                input_file = '%s/%s_%s.%s' % (job_dir, ligand_name, mol_name, file_type)
                # write the smiles string to molecule.smi file
                open(input_file, 'w').write(obj.SmilesStr)
                # convert smi to xyz file
                cmd = '%s -i%s %s -O %s/%s_%s.xyz --gen3D' % (self.obabel, file_type, input_file, job_dir, ligand_name, mol_name)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            if obj.SmilesStrP1:
                file_type = 'smi'

                input_file = '%s/%s_%s.%s' % (job_dir, complex_name, mol_name, file_type)
                # write the smiles string to molecule.smi file
                open(input_file, 'w').write(obj.SmilesStrP1)
                # convert smi to xyz file
                cmd = '%s -i%s %s -O %s/%s_%s.xyz --gen3D' % (self.obabel, file_type, input_file, job_dir, complex_name, mol_name)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            if JobType in ['logk']:
                if obj.SmilesStrM:
                    file_type = 'smi'

                    input_file = '%s/%s_%s.%s' % (job_dir, metal_name, mol_name, file_type)
                    # write the smiles string to molecule.smi file
                    open(input_file, 'w').write(obj.SmilesStrM)
                    # convert smi to xyz file
                    cmd = '%s -i%s %s -O %s/%s_%s.xyz --gen3D' % (self.obabel, file_type, input_file, job_dir, metal_name, mol_name)
                    cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, err = cmd.communicate()

        else:
            if obj.UploadedFile:
                file_name = os.path.basename(obj.UploadedFile.path)
                file_type = obj.UploadedFileType

                uploaded_file = '%s/%s' % (job_dir, file_name)
                input_file = '%s/%s.%s' % (job_dir, mol_name, file_type)
                # copy input file to input.file_type
                shutil.copy(uploaded_file, input_file)

                # convert smi to xyz file
                if file_type not in ['xyz']:
                    cmd = '%s -i%s %s -O %s/%s.xyz' % (self.obabel, file_type, input_file, job_dir, mol_name)
                    cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, err = cmd.communicate()
            else:
                file_type = 'smi'

                input_file = '%s/%s.%s' % (job_dir, mol_name, file_type)
                # write the smiles string to molecule.smi file
                open(input_file, 'w').write(obj.SmilesStr)
                # convert smi to xyz file
                cmd = '%s -i%s %s -O %s/%s.xyz --gen3D' % (self.obabel, file_type, input_file, job_dir, mol_name)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
        return

    def JobExec(self, obj, JobType='csearch'):
        '''
        Currently, run the jobs on this computer.

        '''
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)
        os.chdir(job_dir)

        if JobType in ['csearch']:
            jobscript = 'CSearch.run'
        elif JobType in ['hgspeci']:
            jobscript = 'runPhreeqc.sh'
        else:
            obj.FailedReason += 'Could not find script file for JobType (%s)' % (JobType)
            # change the job status in DB to '3' error
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
            return

        runJob = subprocess.Popen('sh %s' % jobscript, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # execute the script (CSearch.run)
        try:
            # run the calculation
            err, out = runJob.communicate()

            # collect the resutls
            if JobType in ['hgspeci']:
                try:
                    self.HgspeciCollectResults(obj=obj, JobType=JobType)
                except:
                    obj.FailedReason += 'Could not collect the results for (%s)' % str(job_id)
                    # change the job status in DB to '3' error
                    obj.CurrentStatus = '3'
                    obj.Successful = False
                    obj.save()

            # change the job status in DB to '2' finished
            obj.CurrentStatus = '2'
            obj.Successful = True
            obj.FailedReason += ''
            obj.save()
        except:
            obj.FailedReason += 'Could not run the script file (%s)' % jobscript
            # change the job status in DB to '3' error
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
            logging.warn(err)

        return

    def JobExec_v1(self, obj, JobType='csearch'):
        '''
        Submit the job on this computer.
        '''
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)
        os.chdir(job_dir)

        PBSoutput = '0'

        # submit the script
        try:
            PBSoutput = subprocess.check_output(['qsub', 'submit.sh'])
        except:
            PBSoutput = '-1'

        return PBSoutput

    def CheckJob(self, obj, JobType='csearch'):
        '''
        Check the status of the job.
        '''
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)
        os.chdir(job_dir)

        try:
            os.makedirs(job_dir)
        except:
            pass

        # get PBS log files
        # the job name should be in the format of "JobID-JobType"!
        pbs_outfiles = [i for i in os.listdir('.') if i.startswith('%d-%s.o' % (job_id, JobType))]

        if len(pbs_outfiles) > 0:
            # get the latest one
            pbs_outfile = sorted(pbs_outfiles)[-1]
            fout = open(pbs_outfile).readlines()

            if JobType in ['csearch']:
                flag_line = [l for l in fout if l.find("Job is Done!")>=0]

                if len(flag_line) > 0:
                    # change the job status in DB to '2' finished
                    obj.CurrentStatus = '2'
                    obj.save()

            elif JobType in ['csearch_reclustering']:
                flag_line = [l for l in fout if l.find("Reclustering Job is Done!")>=0]

                if len(flag_line) > 0:
                    # change the job status in DB to '2' finished
                    obj.CurrentStatus = '2'
                    obj.save()

        return


    def Zip4Downlaod(self, obj, JobType='csearch'):
        '''
        create the zip file for download
        '''
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)
        os.chdir(job_dir)

        # determine the results directory
        if JobType in ['csearch'] and obj.CSearchType in ['Random']:
            results_dir = '%s-%d' % (JobType, job_id)
        elif JobType in ['csearch'] and obj.CSearchType in ['Replica']:
            results_dir = '%s-%d_results' % (JobType, job_id)
        elif JobType in ['csearch'] and obj.CSearchType in ['DFT']:
            results_dir = '%s-%d' % (JobType, job_id)
        else:
            try:
                os.mkdir('results')
            except:
                pass

            for f in os.listdir('.'):
                if f.endswith('.com') or f.endswith('.nw') or f.endswith('.txt'):
                    try:
                        shutil.copy(f, 'results/')
                    except:
                        pass

            results_dir = 'results'

        # make archive file for download
        try:
            shutil.make_archive('%s-%d' % (JobType, job_id), 'zip', results_dir)
        except:
            obj.FailedReason += 'Could not create zip file (%s.zip).' % results_dir
            # change the job status in DB to '3' error
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
            logging.warn(err)


    #### Csearch ####
    def CSearchJobPrepare(self, obj, JobType='csearch'):
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        # rename the uploaded or input smiles file
        if obj.UploadedFile:
            file_name = os.path.basename(obj.UploadedFile.path)
            file_type = obj.UploadedFileType

            uploaded_file = '%s/%s' % (job_dir, file_name)
            input_file = '%s/%s-%d.%s' % (job_dir, JobType, job_id, file_type)
            # copy input file to input.file_type
            shutil.copy(uploaded_file, input_file)
        else:
            file_type = 'smi'

            input_file = '%s/%s-%d.%s' % (job_dir, JobType, job_id, file_type)
            # write the smiles string to molecule.smi file
            open(input_file, 'w').write(obj.SmilesStr)

        # path of exec and submit script
        exe_file = '%s/CSearch.run' % job_dir
        sub_file = '%s/submit.sh' % job_dir

        # generate the exec script file
        if obj.CSearchType in ['Random']:
            cmd_line = '%s/scripts/CSearchRandom.py --NRotamers %d --Forcefield %s --NStep %d --eps %s ' \
                       '--minSamples %d %s-%d.%s >> CSearch.log 2>&1\n' \
                       'chmod -R g+rw *\n' \
                       'chmod -R g+rw %s-%d\n' \
                       'find . -type d -exec chmod 770 {} +' \
                       % (self.DjangoHome, obj.RandomNRotamers, obj.RandomForcefield, obj.RandomNSteps, str(obj.RandomEPS),
                          obj.RandomNMinSamples, JobType, job_id, file_type, JobType, job_id)
            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason += 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()

            # parameters for job script
            Nnodes = 1
            Nprocessors = 1
        elif obj.CSearchType in ['DFT']:
            # use cp2k
            #cmd_line = '%s/scripts/CSearchRandom.py --NRotamers %d -np %d -xc %s -cutoff %s -vacuum %s -charge %s ' \
            #           '-openshell %s -steps %d -fmax %s -cp2k True --eps %s --minSamples %d %s-%d.%s >> CSearch.log 2>&1\n' \
            #           'chmod -R g+rw %s-%d\n' \
            #           'find . -type d -exec chmod 770 {} +' \
            #           % (self.DjangoHome, obj.RandomNRotamers, obj.DFTProcessors, obj.DFTXC, str(obj.DFTCutoff), str(obj.DFTVacuum),
            #             str(obj.DFTCharge), str(obj.DFTOpenshell), obj.DFTSteps, str(obj.DFTFmax), str(obj.RandomEPS),
            #              obj.RandomNMinSamples, JobType, job_id, file_type,
            #              JobType, job_id)

            cmd_line = '%s/scripts/CSearchRandom.py --NRotamers %d -np %d -method %s -charge %s ' \
                       '-openshell %s -steps %d -fmax %s -mopac True --eps %s --minSamples %d %s-%d.%s >> CSearch.log 2>&1\n' \
                       'chmod -R g+rw *\n' \
                       'chmod -R g+rw %s-%d\n' \
                       'find . -type d -exec chmod 770 {} +' \
                       % (self.DjangoHome, obj.RandomNRotamers, obj.MPProcessors, obj.MPMethod, str(obj.MPCharge),
                          str(obj.MPOpenshell), obj.MPSteps, str(obj.MPFmax), str(obj.RandomEPS),
                          obj.RandomNMinSamples, JobType, job_id, file_type,
                          JobType, job_id)

            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason += 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()

            # parameters for job script
            Nnodes = 1
            Nprocessors = obj.MPProcessors

        elif obj.CSearchType in ['Replica']:
            if obj.ReplicaSolvationType in ['gas']:
                gas = 'True'
                explicit = 'False'
                implicit = 'False'
            elif obj.ReplicaSolvationType in ['wat', 'water']:
                gas = 'False'
                explicit = 'True'
                implicit = 'False'
            elif obj.ReplicaSolvationType in ['gbis']:
                gas = 'False'
                explicit = 'False'
                implicit = 'True'

            cmd_line = '%s/scripts/CSearchReplica.py -np %d -nr %d -nc %d --cutoff %s ' \
                       '--gas=%s --explicit=%s --implicit=%s -t xyz %s-%d.xyz --netcharge %s -o %s-%d >> CSearch.log 2>&1\n' \
                       'chmod -R g+rw *\n' \
                       'chmod -R g+rw %s-%d\n' \
                       'chmod -R g+rw %s-%d_results\n' \
                       'find . -type d -exec chmod 770 {} +' \
                       % (self.DjangoHome, obj.ReplicaProcessors, obj.ReplicaNReplicas, obj.ReplicaNClusters, str(obj.ReplicaClusterCutoff),
                          gas, explicit, implicit, JobType, job_id, obj.ReplicaNetCharge, JobType, job_id,
                          JobType, job_id,
                          JobType, job_id)
            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason += 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()

            # parameters for job script
            Nnodes = 1
            Nprocessors = int(obj.ReplicaProcessors)

        # generate the submit file
        # the job name should be in the format of "JobID-JobType"!
        sub_str = '''#!/bin/bash
#PBS -N %d-%s
#PBS -l nodes=%d:ppn=%d
#PBS -j oe
#PBS -l walltime=24:00:00
#PBS -W umask=0007
#PBS -W group_list=www-data

cd $PBS_O_WORKDIR

# run the job
./CSearch.run

# signal
echo "Job is Done!"
        ''' % (job_id, JobType, Nnodes, Nprocessors)

        # write the sub_file
        try:
            sub_filehandle = open(sub_file, 'w')
            sub_filehandle.write(sub_str + '\n')
            sub_filehandle.close()
        except:
            obj.FailedReason += 'Could not generate submit file (submit.sh)'
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()

        return

    def CSearchJobReclustering(self, obj, JobType='csearch'):
        # get basic info
        job_id = obj.JobID
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        # rename the uploaded or input smiles file
        if obj.UploadedFile:
            file_name = os.path.basename(obj.UploadedFile.path)
            file_type = obj.UploadedFileType

            uploaded_file = '%s/%s' % (job_dir, file_name)
            input_file = '%s/%s-%d.%s' % (job_dir, JobType, job_id, file_type)
            # copy input file to input.file_type
            shutil.copy(uploaded_file, input_file)
        else:
            file_type = 'smi'

            input_file = '%s/%s-%d.%s' % (job_dir, JobType, job_id, file_type)
            # write the smiles string to molecule.smi file
            open(input_file, 'w').write(obj.SmilesStr)

        # path of exec and submit script
        exe_file = '%s/CSearch.run' % job_dir
        sub_file = '%s/submit.sh' % job_dir


        # generate the exec script file
        if obj.CSearchType in ['Random']:
            cmd_line = '%s/scripts/CSearchRandom.py --eps %s ' \
                       '--minSamples %d reclustering %s-%d.%s >> CSearch-reclustering.log 2>&1\n' \
                       'chmod -R 770 %s-%d\n' \
                       'find . -type d -exec chmod 770 {} +' \
                       % (self.DjangoHome, str(obj.RandomEPS),
                          obj.RandomNMinSamples, JobType, job_id, file_type, JobType, job_id)
            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason += 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()

        # generate the submit file
        # the job name should be in the format of "JobID-JobType"!
        sub_str = '''#!/bin/bash
#PBS -N %d-%s
#PBS -l nodes=1:ppn=1
#PBS -j oe
#PBS -l walltime=24:00:00
#PBS -W umask=0007
#PBS -W group_list=www-data

cd $PBS_O_WORKDIR

# run the job
./CSearch.run

# signal
echo "Reclustering Job is Done!"
        ''' % (job_id, JobType)

        # write the sub_file
        try:
            sub_filehandle = open(sub_file, 'w')
            sub_filehandle.write(sub_str + '\n')
            sub_filehandle.close()
        except:
            obj.FailedReason += 'Could not generate submit file (submit.sh)'
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
        return


    #### Hgspeci ####
    def HgspeciJobPrepare(self, obj, JobType='hgspeci'):
        # get basic info
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        phreeqc = PhreeqcPrepare()
        try:
            phreeqc.genInputFile(obj=obj, outdir=job_dir)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for phreeqc'
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e
        try:
            phreeqc.genDatabaseFile(obj=obj, outdir=job_dir)
            obj.Successful = True
        except:
            obj.FailedReason += 'Could not generate database file for phreeqc.'
            obj.CurrentStatus = '3'
            obj.Successful = False
        try:
            phreeqc.genJobScript(obj=obj, outdir=job_dir)
            obj.Successful = True
        except:
            obj.FailedReason += 'Could not generate job script for running phreeqc.'
            obj.CurrentStatus = '3'
            obj.Successful = False

        obj.save()
        return

    def HgspeciCollectResults(self, obj, JobType='hgspeci'):
        # get basic info
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        phreeqc = PhreeqcPrepare()
        try:
            phreeqc.collectResults(obj=obj, outdir=job_dir)
            obj.Successful = True
        except:
            print 'Could not collect the speciation data from the output file.'

        obj.save()
        return

    #### Gsolv ####
    def GsolvJobPrepare(self, obj, JobType='gsolv'):
        # get basic info
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMCalculationPrepare()

        # generate the conf dict
        try:
            conf, conf_gas = qmclac.gen_conf_dict(obj)
            obj.Successful = True
        except:
            obj.FailedReason += 'Could not generate configuration dict for %s.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False

        # generate the input files
        try:
            if obj.QMSoftware in ['Gaussian']:
                inp = qmclac.gen_g09input(conf)
            elif obj.QMSoftware in ['NWChem']:
                inp = qmclac.gen_NWinput(conf)
            elif obj.QMSoftware in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for %s.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftware in ['Gaussian']:
                fout = open('%s/%s-%s_aq.com' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['NWChem']:
                fout = open('%s/%s-%s_aq.nw' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['Arrows']:
                fout = open('%s/%s-%s_aq.arrows' % (job_dir, JobType, obj.JobID), 'w')
            fout.write(inp)
            fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for %s.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False
        # generate the input files for gas phase
        try:
            if obj.QMSoftware in ['Gaussian']:
                inp_gas = qmclac.gen_g09input(conf_gas)
            elif obj.QMSoftware in ['NWChem']:
                inp_gas = qmclac.gen_NWinput(conf_gas)
            elif obj.QMSoftware in ['Arrows']:
                inp_gas = qmclac.gen_Arrowsinput(conf_gas)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for %s in gas phase' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file in gas phase: %s' % e
        try:
            # write input file
            if obj.QMSoftware in ['Gaussian']:
                fout = open('%s/%s-%s_gas.com' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['NWChem']:
                fout = open('%s/%s-%s_gas.nw' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['Arrows']:
                fout = open('%s/%s-%s_gas.arrows' % (job_dir, JobType, obj.JobID), 'w')
            fout.write(inp_gas)
            fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for %s in gas phase.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False


        if obj.QMSoftware in ['Arrows']:
            mail_subject = '%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for %s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False

            try:
                send_mail(mail_subject, inp_gas, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for %s_%s in gas phase. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False

        obj.save()
        return

    def GsolvCollectResults(self, obj, JobType='gsolv'):
        # get basic info
        JobLocation = '%s/gsolv/jobs' % (self.JobLocation)
        job_dir = '%s/%s/%s/' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMResultsCalculation()
        # path for the output files
        aq_out = job_dir + os.path.basename(obj.UploadedOutputFile.file.name)
        gas_out = job_dir + os.path.basename(obj.UploadedOutputFileP1.file.name)

        # output file existence
        if not os.path.exists(aq_out):
            obj.FailedReason += ' Output file for the molecule in aqueous phase is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False
        if not os.path.exists(gas_out):
            obj.FailedReason += ' Output file for the molecule in gas phase is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False

        # The output is from Gaussian or NWChem
        obj.QMSoftwareOutput = qmclac.QMSoftware(aq_out)
        obj.QMSoftwareOutputP1 = qmclac.QMSoftware(gas_out)

        # calculate the logK
        try:
            Gsolv, Gaq, Ggas = qmclac.Calc_Gsolv(obj)
        except:
            obj.FailedReason += ' Failed to calculate the Gsolv for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        obj.EnergyfromOutputFiles = str(Gaq)
        obj.EnergyfromOutputFilesP1 = str(Ggas)
        obj.GsolvCorrected = Gsolv
        obj.CurrentStatus = '2'
        obj.Successful = True

        obj.save()

        # write down the calculated constants
        result_dir = '%s/results' % job_dir
        result_file = '%s/%s-%s_constants.txt' % (result_dir, str(JobType), str(obj.JobID))
        try:
            os.makedirs(result_dir)
        except:
            pass

        out_txt = '''The absolute free energy for the molecule in GAS phase is: %s kcal/mol
The absolute free energy for the molecule in SOLUTION is: %s kcal/mol
The standard state correction factor at 298 K is: 1.89 kcal/mol
The calculated solvation free energy is: %s kcal/mol
\n''' % (str(Ggas), str(Gaq), str(Gsolv))

        try:
            fout = open(result_file, 'w')
            fout.write(out_txt)
            fout.close()
        except Exception as e:
            obj.FailedReason += ' Failed to write calculated constants for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        return

    #### pKa ####
    def pKaJobPrepare(self, obj, JobType='pka'):
        # get basic info
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMCalculationPrepare()

        # generate the conf dicts
        try:
            conf_A, conf_HA = qmclac.gen_conf_dict(obj)
            obj.Successful = True
        except:
            obj.FailedReason += 'Could not generate configuration dict for A_%s_%s.' % (JobType,obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False


        #### generate the input files for conf_A
        try:
            if obj.QMSoftware in ['Gaussian']:
                inp = qmclac.gen_g09input(conf_A)
            elif obj.QMSoftware in ['NWChem']:
                inp = qmclac.gen_NWinput(conf_A)
            elif obj.QMSoftware in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf_A)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for A_%s_%s' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftware in ['Gaussian']:
                fout = open('%s/A_%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['NWChem']:
                fout = open('%s/A_%s-%s.nw' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftware in ['Arrows']:
                fout = open('%s/A_%s-%s.arrows' % (job_dir, JobType, obj.JobID), 'w')
            fout.write(inp)
            fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for A_%s_%s.' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        if obj.QMSoftware in ['Arrows']:
            mail_subject = 'A_%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for A_%s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False


        #### generate the input files for conf_HA
        try:
            if obj.QMSoftwareP1 in ['Gaussian']:
                inp = qmclac.gen_g09input(conf_HA)
            elif obj.QMSoftwareP1 in ['NWChem']:
                inp = qmclac.gen_NWinput(conf_HA)
            elif obj.QMSoftwareP1 in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf_HA)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for HA_%s_%s' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftwareP1 in ['Gaussian']:
                fout = open('%s/HA_%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftwareP1 in ['NWChem']:
                fout = open('%s/HA_%s-%s.nw' % (job_dir, JobType, obj.JobID), 'w')
            elif obj.QMSoftwareP1 in ['Arrows']:
                fout = open('%s/HA_%s-%s.arrows' % (job_dir, JobType, obj.JobID), 'w')
            fout.write(inp)
            fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for HA_%s_%s.' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        if obj.QMSoftwareP1 in ['Arrows']:
            mail_subject = 'HA_%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for HA_%s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False

        obj.save()
        return

    def pKaCollectResults(self, obj, JobType='pka'):
        # get basic info
        JobLocation = '%s/pka/jobs' % (self.JobLocation)
        job_dir = '%s/%s/%s/' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMResultsCalculation()
        # path for the output files
        A_out = job_dir + os.path.basename(obj.UploadedOutputFile.file.name)
        HA_out = job_dir + os.path.basename(obj.UploadedOutputFileP1.file.name)

        # output file existence
        if not os.path.exists(A_out):
            obj.FailedReason += ' Output file for deprotonated form (A) is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False
        if not os.path.exists(HA_out):
            obj.FailedReason += ' Output file for protonated form (HA) is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False

        # The output is from Gaussian or NWChem
        obj.QMSoftwareOutput = qmclac.QMSoftware(A_out)
        obj.QMSoftwareOutputP1 = qmclac.QMSoftware(HA_out)

        # calculate the pKa
        try:
            pKa, Gaq_A, Gaq_HA = qmclac.Calc_pKa(obj)
        except:
            obj.FailedReason += ' Failed to calculate the pKa for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        obj.EnergyfromOutputFiles = str(Gaq_A)
        obj.EnergyfromOutputFilesP1 = str(Gaq_HA)
        obj.PKafromOutputFiles = pKa
        obj.CurrentStatus = '2'
        obj.Successful = True

        obj.save()

        # write down the calculated constants
        result_dir = '%s/results' % job_dir
        result_file = '%s/%s-%s_constants.txt' % (result_dir, str(JobType), str(obj.JobID))
        try:
            os.makedirs(result_dir)
        except:
            pass

        out_txt = '''The absolute solvation free energy for molecule A- is: %s kcal/mol
The absolute solvation free energy for molecule HA is: %s kcal/mol
The experimentally measured absolute solvation free energy for H+ is: -270.30 kcal/mol
The standard state correction factor at 298 K is: 1.89 kcal/mol
The calculated pKa is: %s
\n''' % (str(Gaq_A), str(Gaq_HA), str(pKa))

        try:
            fout = open(result_file, 'w')
            fout.write(out_txt)
            fout.close()
        except Exception as e:
            obj.FailedReason += ' Failed to write calculated constants for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        return

    #### logK ####
    def LogKJobPrepare(self, obj, JobType='logk'):
        # get basic info
        JobLocation = '%s/%s/jobs' % (self.JobLocation, JobType)
        job_dir = '%s/%s/%s' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMCalculationPrepare()

        # generate the conf dicts
        try:
            conf_L, conf_ML, conf_M, conf_L_link1, conf_ML_link1, conf_M_link1 = qmclac.gen_conf_dict(obj)
            obj.Successful = True
        except:
            obj.FailedReason += 'Could not generate configuration dict for L_%s_%s.' % (JobType,obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False


        #### generate the input files for conf_L
        try:
            if obj.QMSoftware in ['Gaussian']:
                inp = qmclac.gen_g09input(conf_L)
                inp_link1 = qmclac.gen_g09input(conf_L_link1)
                inp_link1 = '\n'.join([i.replace('step2_', 'step1_') for i in inp_link1.split('\n') if not i.startswith("%OldChk")])
            elif obj.QMSoftware in ['NWChem']:
                inp = qmclac.gen_NWinput(conf_L)
            elif obj.QMSoftware in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf_L)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for L_%s_%s' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftware in ['Gaussian']:
                fout = open('%s/L_%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.write('\n--link1--\n')
                fout.write(inp_link1)
                fout.close()
            elif obj.QMSoftware in ['NWChem']:
                fout = open('%s/L_%s-%s.nw' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()
            elif obj.QMSoftware in ['Arrows']:
                fout = open('%s/L_%s-%s.arrows' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for L_%s_%s.' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        if obj.QMSoftware in ['Arrows']:
            mail_subject = 'L_%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for L_%s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False


        #### generate the input files for conf_ML
        try:
            if obj.QMSoftwareP1 in ['Gaussian']:
                inp = qmclac.gen_g09input(conf_ML)
                inp_link1 = qmclac.gen_g09input(conf_ML_link1)
                inp_link1 = '\n'.join([i.replace('step2_', 'step1_') for i in inp_link1.split('\n') if not i.startswith("%OldChk")])
            elif obj.QMSoftwareP1 in ['NWChem']:
                inp = qmclac.gen_NWinput(conf_ML)
            elif obj.QMSoftwareP1 in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf_ML)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for ML_%s_%s' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftwareP1 in ['Gaussian']:
                fout = open('%s/ML_%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.write('\n--link1--\n')
                fout.write(inp_link1)
                fout.close()
            elif obj.QMSoftwareP1 in ['NWChem']:
                fout = open('%s/ML_%s-%s.nw' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()
            elif obj.QMSoftwareP1 in ['Arrows']:
                fout = open('%s/ML_%s-%s.arrows' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for ML_%s_%s.' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        if obj.QMSoftwareP1 in ['Arrows']:
            mail_subject = 'ML_%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for ML_%s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False

        #### generate the input files for conf_M
        try:
            if obj.QMSoftwareM in ['Gaussian']:
                inp = qmclac.gen_g09input(conf_M)
                inp_link1 = qmclac.gen_g09input(conf_M_link1)
                inp_link1 = '\n'.join([i.replace('step2_', 'step1_') for i in inp_link1.split('\n') if not i.startswith("%OldChk")])
            elif obj.QMSoftwareM in ['NWChem']:
                inp = qmclac.gen_NWinput(conf_M)
            elif obj.QMSoftwareM in ['Arrows']:
                inp = qmclac.gen_Arrowsinput(conf_M)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason += 'Could not generate input file for M_%s_%s' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            if obj.QMSoftwareM in ['Gaussian']:
                fout = open('%s/M_%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.write('\n--link1--\n')
                fout.write(inp_link1)
                fout.close()
            elif obj.QMSoftwareM in ['NWChem']:
                fout = open('%s/M_%s-%s.nw' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()
            elif obj.QMSoftwareM in ['Arrows']:
                fout = open('%s/M_%s-%s.arrows' % (job_dir, JobType, obj.JobID), 'w')
                fout.write(inp)
                fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason += 'Could not write the input file for M_%s_%s.' % (JobType, obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        if obj.QMSoftwareM in ['Arrows']:
            mail_subject = 'M_%s_%s' % (JobType, obj.JobID)
            from_address = 'plian@utk.edu'
            to_address = ['arrows@emsl.pnnl.gov']
            try:
                send_mail(mail_subject, inp, from_address, to_address, fail_silently=False)
                obj.Successful = True
                obj.CurrentStatus = '1'
            except Exception as e:
                obj.FailedReason += 'Could not send emails for M_%s_%s. (%s)' % (JobType, obj.JobID, e)
                obj.CurrentStatus = '3'
                obj.Successful = False



        obj.save()
        return conf_L_link1

    def LogKCollectResults(self, obj, JobType='logk'):
        # get basic info
        JobLocation = '%s/logk/jobs' % (self.JobLocation)
        job_dir = '%s/%s/%s/' % (self.DjangoHome, JobLocation, obj.JobID)

        try:
            os.makedirs(job_dir)
        except:
            pass

        qmclac = QMResultsCalculation()
        # path for the output files
        L_out = job_dir + os.path.basename(obj.UploadedOutputFile.file.name)
        ML_out = job_dir + os.path.basename(obj.UploadedOutputFileP1.file.name)
        M_out = job_dir + os.path.basename(obj.UploadedOutputFileM.file.name)

        # output file existence
        if not os.path.exists(L_out):
            obj.FailedReason += ' Output file for the Ligand (L-) is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False
        if not os.path.exists(ML_out):
            obj.FailedReason += ' Output file for the Complex (ML) is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False
        if not os.path.exists(M_out):
            obj.FailedReason += ' Output file for the Metal (M) is not exist!'
            obj.CurrentStatus = '3'
            obj.Successful = False

        # The output is from Gaussian or NWChem
        obj.QMSoftwareOutput = qmclac.QMSoftware(L_out)
        obj.QMSoftwareOutputP1 = qmclac.QMSoftware(ML_out)
        obj.QMSoftwareOutputM = qmclac.QMSoftware(M_out)

        # calculate the logK
        try:
            logK, Gaq_L, Gaq_ML, Gaq_M = qmclac.Calc_logK(obj)
        except:
            obj.FailedReason += ' Failed to calculate the log K for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        obj.EnergyfromOutputFiles = str(Gaq_L)
        obj.EnergyfromOutputFilesP1 = str(Gaq_ML)
        obj.EnergyfromOutputFilesM = str(Gaq_M)
        obj.LogKfromOutputFiles = logK
        obj.CurrentStatus = '2'
        obj.Successful = True

        obj.save()

        # write down the calculated constants
        result_dir = '%s/results' % job_dir
        result_file = '%s/%s-%s_constants.txt' % (result_dir, str(JobType), str(obj.JobID))
        try:
            os.makedirs(result_dir)
        except:
            pass

        out_txt = '''The absolute solvation free energy for molecule L- is: %s kcal/mol
The absolute solvation free energy for molecule ML is: %s kcal/mol
The absolute solvation free energy for molecule M+ is: %s kcal/mol
The standard state correction factor at 298 K is: 1.89 kcal/mol
The calculated log K is: %s
\n''' % (str(Gaq_L), str(Gaq_ML), str(Gaq_M), str(logK))

        try:
            fout = open(result_file, 'w')
            fout.write(out_txt)
            fout.close()
        except Exception as e:
            obj.FailedReason += ' Failed to write calculated constants for job %s!' % str(obj.JobID)
            obj.CurrentStatus = '3'
            obj.Successful = False

        return

if __name__ == '__main__':
    print("This is JobManager")