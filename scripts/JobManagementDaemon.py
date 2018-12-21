#!/usr/bin/env python
import os, time, datetime, logging, django, subprocess
from django.db.models import Q
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
django.setup()

from cyshg.models import AllJobIDs
from csearch.models import CSearchJob

class JobManagementDaemon:
    def __init__(self):
        self.DjangoHome = '/home/p6n/workplace/website/cyshg'
        self.obabel = '/home/p6n/anaconda2/bin/obabel'
        self.JobLocation = 'media'


    def submit(self, obj):
        # get basic info
        if obj.JobType in ['toolkit']:
            JobType = obj.SubJobType
        else:
            JobType = obj.JobType
        job_dir = '%s/%s/%s/jobs/%s' % (self.DjangoHome, self.JobLocation, JobType, obj.JobID)

        logging.info('Enter into directory %s' % job_dir)

        # change the right of the job dir
        os.system("sudo chown -R p6n %s" % job_dir)
        os.system("sudo chmod -R 774 %s" % job_dir)
        os.chdir(job_dir)
#        os.system("qsub submit.sh")

        csearchJob = CSearchJob.objects.get(JobID=obj.JobID)

        PBSoutput = '0'
        # submit the script
        try:
            PBSoutput = subprocess.check_output(['qsub', 'submit.sh'])
            logging.info('Job (%s, %s) submitted.' % (JobType, obj.JobID))

        except:
            PBSoutput = '-1'
        csearchJob.PBSID = PBSoutput
        csearchJob.save()

    def monitor(self, Modules=['csearch'], Interval=15):
        while True:
            startT = time.time()
            # get all job ids
            # NOTE: AlllJobIDs is different from CSearchJOB!!!
            alljobs = AllJobIDs.objects.filter(Q(JobType__in=Modules) | Q(SubJobType__in=Modules))

            # unmark empty jobs that longer then 24 hours.
            # BUG: The timezone for some python datetime maybe wrong, so its safe to give a 24 hours difference
            for j in alljobs:
                deltaT = int(datetime.datetime.now().strftime('%s')) - int(j.CreatedDate.strftime('%s'))
                if deltaT > 3600 * 24:
                    j.CurrentStatus = '2'
                    j.save()

            jobs_tobestarted = [i for i in alljobs if i.CurrentStatus == '0']
            if len(jobs_tobestarted) == 0:
                #logging.info('No to-be-start job is found from AllJobIDs.')
                time.sleep(Interval)
                continue

            logging.info(jobs_tobestarted)
            # check and submit each job
            for job in jobs_tobestarted:
                logging.info('Checking Job: %s' % (str(job.JobID)))

                if job.JobType in ['toolkit']:
                    JobType = job.SubJobType
                else:
                    JobType = job.JobType

                # get job from CSearchJob according to JobID
                if JobType in ['csearch']:
                    sub_job = CSearchJob.objects.get(JobID=job.JobID)
                else:
                    continue

                # if job status in csearch job db is running, then submit it, else skip
                if sub_job.CurrentStatus == '1':
                    try:
                        # do something to submit the job
                        self.submit(job)
                        # change the job status to finished
                        job.CurrentStatus = '2'
                        job.save()
                    except Exception as e:
                        logging.error('Failed to submit job, the error is:\n%s' % e)
                        # change the job status to something wrong
                        job.CurrentStatus = '3'
                        job.save()

            # wait for next check
            time.sleep(Interval)
            logging.info('Waited for %.2f seconds at %s\n' % (time.time()-startT, time.ctime()))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('The Job Management Daemon is started at %s' % datetime.datetime.now())
    logging.info('''Note: this script should be run by who has the sudo right.\nNote: This script checks AlllJobIDs instead of CSearchJOB to determine submit or not!!!
    ''')
    daemon = JobManagementDaemon()
    daemon.monitor(Modules=['csearch'], Interval=15)
