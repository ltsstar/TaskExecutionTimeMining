#!/bin/bash
cd data

bpic_2012="https://data.4tu.nl/ndownloader/items/533f66a4-8911-4ac7-8612-1235d65d1f37/versions/1"
wget -O bpic_2012.zip "$bpic_2012"
unzip -o bpic_2012.zip
rm DATA.xml
gunzip -f BPI_Challenge_2012.xes.gz
rm bpic_2012.zip


bpic_2017="https://data.4tu.nl/ndownloader/items/34c3f44b-3101-4ea9-8281-e38905c68b8d/versions/1"
wget -O bpic_2017.zip "$bpic_2017"
unzip -o bpic_2017.zip
rm DATA.xml
gunzip -f 'BPI Challenge 2017.xes.gz'
rm bpic_2017.zip
