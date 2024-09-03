#!/bin/sh
current_dir=${PWD##*/}

i=0
for subdir in ./*/; do
	if [ -d "$subdir" ]; then
		if [ -f "$subdir/train.sh" ]; then
			sbatch sbatch.sh $subdir
			echo "Processing directory: $subdir"
			((i++))
		fi
	fi
done
