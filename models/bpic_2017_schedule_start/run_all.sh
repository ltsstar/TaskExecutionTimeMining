#!/bin/sh
current_dir=${PWD##*/}

i=0
for subdir in ./*/; do
	if [ -d "$subdir" ]; then
		cd $subdir
		screen -S "$current_dir.$i" -d -m bash
		screen -r "$current_dir.$i" -X stuff "./train.sh"$(echo -ne '\015')
		cd ..
		echo "Processing directory: $subdir"
		((i++))
	fi
done
