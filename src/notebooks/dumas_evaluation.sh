#!/bin/bash
jupyter nbconvert --execute --to notebook --inplace BPIC_2017/BPIC_2017_dumas_evaluation.ipynb --ExecutePreprocessor.timeout=-1
