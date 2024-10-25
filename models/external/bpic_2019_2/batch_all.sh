#!/bin/sh
current_dir=${PWD##*/}

i=0
for subdir in ./*/; do
	if [ -d "$subdir" ]; then
		if [[ "$subdir$" == *"resource_count"* || "$subdir$" == *"resource-count"* || "$subdir$" == *"resoure-count"* ]]; then
			if [ -f "$subdir/train.sh" ]; then
				sbatch sbatch48.sh $subdir
				echo "Processing directory 48GB: $subdir"
				#((i++))
			fi
		else
			if [ -f "$subdir/train.sh" ]; then
				sbatch sbatch16.sh $subdir
				echo "Processing directory 16GB: $subdir"
				((i++))
			fi
		fi
	fi
done
