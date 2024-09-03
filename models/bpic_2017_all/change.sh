#!/bin/bash

# Function to replace values in a file
replace_values() {
  local file="$1"
  local src_location_pattern="file_location <- '.*'"
  local new_src_location="file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'"
  local old_nburn_pattern="nburn <- [0-9]*"
  local new_nburn="nburn <- 25000"
  local old_nsim_pattern="nsim <- [0-9]*"
  local new_nsim="nsim <- 150"
  local old_nthin_pattern="nthin <- [0-9]*"
  local new_nthin="nthin <- 150"

  # Use sed to perform in-place substitutions with regular expressions
  sed -i "s/$old_nburn_pattern/$new_nburn/g" "$file"
  sed -i "s/$old_nsim_pattern/$new_nsim/g" "$file"
  sed -i "s/$old_nthin_pattern/$new_nthin/g" "$file"
  sed -i "s|$src_location_pattern|$new_src_location|g" "$file"
}

# Loop through all subdirectories
find . -type f -name "drbart_variable.r" | while read -r file; do
    # Replace values in the file
    replace_values "$file"
    echo "Replaced values in $file"
done

echo "Finished processing subdirectories."
