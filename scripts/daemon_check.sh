#!/bin/bash

# used by ROOT to check if the daemon.py is running or not.

# find daemon process
Num_proc=`ps -f -u p6n | grep daemon.py | wc -l`
checking_log="/home/p6n/workplace/website/cyshg/daemon_checking.log"

if [ $Num_proc -eq 1 ]; then
    #echo `date`: 'daemon.py is running!' >> $checking_log
    :
else
    echo `date`: 'daemon.py is dead! Restart it now.' >> $checking_log
    su p6n -c 'cd /home/p6n/workplace/website/cyshg; /home/p6n/anaconda2/bin/python ./daemon.py > log 2>&1 &'
fi

