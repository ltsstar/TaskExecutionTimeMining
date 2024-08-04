#!/bin/bash
cd data

bpic_2012="https://data.4tu.nl/ndownloader/items/533f66a4-8911-4ac7-8612-1235d65d1f37/versions/1"
wget -O bpic_2012.zip "$bpic_2012"
unzip -o bpic_2012.zip
rm DATA.xml
gunzip -f BPI_Challenge_2012.xes.gz
rm bpic_2012.zip
