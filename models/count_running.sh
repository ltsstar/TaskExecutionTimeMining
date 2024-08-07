#!/bin/bash
ps -ax | grep train.sh | wc -l | awk '{$0=$0-1;print}'
