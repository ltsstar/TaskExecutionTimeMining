#!/bin/sh
current_dir=${PWD##*/}

find . -type f -regextype posix-extended -regex ".*\.(txt|json)$" -exec rm {} \;

i=0
for subdir in ./*/; do
	if [ -d "$subdir" ]; then
		cd $subdir
		screen -S "$current_dir.$i" -d -m bash
		screen -r "$current_dir.$i" -X stuff "./train_screen.sh"$(echo -ne '\015')
		cd ..
		echo "Processing directory: $subdir"
		((i++))
	fi
done
