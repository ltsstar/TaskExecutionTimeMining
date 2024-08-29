#!/bin/bash
find . -type f -exec sed -i  "s/y_value <- 'duration_ms_log'/y_value <- 'duration_ms_log'/g" {} +
