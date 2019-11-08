#!/bin/bash

# used by ROOT to check if the daemon.py is running or not.

# find daemon process
Num_proc=`ps -f -u p6n | grep daemon.py | grep -v grep | wc -l`
checking_log="/home/p6n/workplace/website/cyshg/daemon_checking.log"

if [ $Num_proc -eq 1 ]; then
    #echo `date`: 'daemon.py is running!' >> $checking_log
    :
elif [ $Num_proc -gt 1 ]; then
    for i in `ps -f -u p6n | grep daemon.py | grep -v grep | awk '{print $2}'`; do kill $i; done
    echo `date`: 'More than one daemon.py is running! Clean all and restart now.' >> $checking_log
    su p6n -c 'cd /home/p6n/workplace/website/cyshg; /home/p6n/anaconda2/bin/python ./daemon.py > log 2>&1 &'
else
    echo `date`: 'daemon.py is dead! Restart it now.' >> $checking_log
    su p6n -c 'cd /home/p6n/workplace/website/cyshg; /home/p6n/anaconda2/bin/python ./daemon.py > log 2>&1 &'
fi


chmod 664 /home/p6n/workplace/website/cyshg/debug.log


# Check pbs daemons
Check_pbs(){
    Num_proc=`ps -f -u root | grep $1 | grep -v grep | wc -l`

    if [ $Num_proc -eq 1 ]; then
        #echo `date`: "$1 is running!" >> $checking_log
        :
    else
        echo `date`: "$1 is dead! Restart it now." >> $checking_log
        /usr/sbin/$1 >> $checking_log 2>&1
    fi
}

# check the daemons pbs_server pbs_sched pbs_mom
for i in pbs_server pbs_sched pbs_mom
do
    Check_pbs $i;
done
