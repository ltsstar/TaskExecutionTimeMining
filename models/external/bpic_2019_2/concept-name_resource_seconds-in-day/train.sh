#!/bin/bash


# Start or restart the process


port=$(cat ./coordinator)
if [[ -n $(find . -maxdepth 1 -name "ckpt_*.dmtcp") ]]; then
	echo 'continue...'
	ckpt_file=$(find . -name "*.dmtcp" -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f2-)
	#set -m
	dmtcp_restart --join-coordinator --coord-port $port --coord-host "127.0.0.1" $ckpt_file &
	#./dmtcp_restart_script.sh --coord-port $port --coord-host 127.0.0.1
else
	echo 'start new...'
    dmtcp_launch --join-coordinator --port $port -j sh /dss/dsshome1/00/ge35xof4/TaskExecutionTimeMining/src/DRBartModelTrainer/train_dr_bart.sh /dss/dsshome1/00/ge35xof4/TaskExecutionTimeMining/src/TaskExecutionTimeMining/drbart_static.r &
fi

echo "running"
echo "($1 - 0.5) * 3600" | bc | xargs sleep
echo "creating checkpoint..."
port=$(cat ./coordinator)
dmtcp_command --checkpoint --port $port

