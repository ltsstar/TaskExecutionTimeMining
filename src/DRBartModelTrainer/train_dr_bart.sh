#! /bin/bash

dr_bart_variable="drbart_variable.r"
dr_bart_static="$1"

dr_bart_full_name="drbart_full.r"

cat "$dr_bart_variable" > "$dr_bart_full_name"
echo "" >> "$dr_bart_full_name"
cat "$dr_bart_static" >> "$dr_bart_full_name"

R -f "$dr_bart_full_name"