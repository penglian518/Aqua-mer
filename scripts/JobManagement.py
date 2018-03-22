import os, shutil, subprocess, logging
from .PhreeqcPrepare import PhreeqcPrepare
from .QMCalculationPrepare import QMCalculationPrepare

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
            obj.FailedReason = 'Could not find script file (%s) for JobType (%s)' % (jobscript, JobType)
            # change the job status in DB to '3' error
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
            logging.warn(err)
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
                    obj.FailedReason = 'Could not collect the results for (%s)' % str(job_id)
                    # change the job status in DB to '3' error
                    obj.CurrentStatus = '3'
                    obj.Successful = False
                    obj.save()

            # change the job status in DB to '2' finished
            obj.CurrentStatus = '2'
            obj.Successful = True
            obj.FailedReason = ''
            obj.save()
        except:
            obj.FailedReason = 'Could not run the script file (%s)' % jobscript
            # change the job status in DB to '3' error
            obj.CurrentStatus = '3'
            obj.Successful = False
            obj.save()
            logging.warn(err)

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

        # make archive file for download
        dir_download = '%s-%d' % (JobType, job_id)
        try:
            shutil.make_archive('%s-%d' % (JobType, job_id), 'zip', dir_download)
        except:
            obj.FailedReason = 'Could not create zip file (%s-%d.zip).' % (JobType, job_id)
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

        # exec script
        exe_file = '%s/CSearch.run' % job_dir


        if obj.CSearchType in ['Random']:
            cmd_line = '%s/scripts/CSearchRandom.py --NRotamers %d --Forcefield %s --NStep %d --eps %s ' \
                       '--minSamples %d %s-%d.%s >> CSearch.log 2>&1' \
                       % (self.DjangoHome, obj.RandomNRotamers, obj.RandomForcefield, obj.RandomNSteps, str(obj.RandomEPS),
                          obj.RandomNMinSamples, JobType, job_id, file_type)
            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason = 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()
                logging.warn(err)
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

        # exec script
        exe_file = '%s/CSearch.run' % job_dir



        if obj.CSearchType in ['Random']:
            cmd_line = '%s/scripts/CSearchRandom.py --eps %s ' \
                       '--minSamples %d reclustering %s-%d.%s >> CSearch-reclustering.log 2>&1' \
                       % (self.DjangoHome, str(obj.RandomEPS),
                          obj.RandomNMinSamples, JobType, job_id, file_type)
            # write the command line to exe_file
            try:
                exe_filehandle = open(exe_file, 'w')
                exe_filehandle.write(cmd_line + '\n')
                exe_filehandle.close()
            except:
                obj.FailedReason = 'Could not generate commandline file (CSearch.run)'
                obj.CurrentStatus = '3'
                obj.Successful = False
                obj.save()
                logging.warn(err)
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
            obj.FailedReason = 'Could not generate input file for phreeqc'
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e
        try:
            phreeqc.genDatabaseFile(obj=obj, outdir=job_dir)
            obj.Successful = True
        except:
            obj.FailedReason = 'Could not generate database file for phreeqc.'
            obj.CurrentStatus = '3'
            obj.Successful = False
        try:
            phreeqc.genJobScript(obj=obj, outdir=job_dir)
            obj.Successful = True
        except:
            obj.FailedReason = 'Could not generate job script for running phreeqc.'
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

        try:
            conf = qmclac.gen_conf_dict(obj)
            obj.Successful = True
        except:
            obj.FailedReason = 'Could not generate configuration dict for %s.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False

        try:
            inp = qmclac.gen_g09input(conf)
            obj.Successful = True
        except Exception as e:
            obj.FailedReason = 'Could not generate input file for %s' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False
            print 'Could not generate input file: %s' % e

        try:
            # write input file
            fout = open('%s/%s-%s.com' % (job_dir, JobType, obj.JobID), 'w')
            fout.write(inp)
            fout.close()

            obj.Successful = True
            obj.CurrentStatus = '2'
        except:
            obj.FailedReason = 'Could not write the input file for %s.' % JobType
            obj.CurrentStatus = '3'
            obj.Successful = False

        obj.save()
        return

    def GsolvCollectResults(self, obj, JobType='gsolv'):
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

