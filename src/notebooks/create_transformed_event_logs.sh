#!/bin/bash
cd Artificial_Example
jupyter nbconvert --to python Artificial_event_log_transformer.ipynb
python Artificial_event_log_transformer.py
rm Artificial_event_log_transformer.py
cd ..

cd BPIC_2017
jupyter nbconvert --to python BPIC_2017_event_log_transformer.ipynb
python BPIC_2017_event_log_transformer.py
rm BPIC_2017_event_log_transformer.py

jupyter nbconvert --to python BPIC_2017_event_log_transformer-resume_suspend.ipynb
python BPIC_2017_event_log_transformer-resume_suspend.py
rm BPIC_2017_event_log_transformer-resumse_suspend.py

jupyter nbconvert --to python BPIC_2017_event_log_waiting_transformer.ipynb
python BPIC_2017_event_log_waiting_transformer.py
rm BPIC_2017_event_log_waiting_transformer.py

jupyter nbconvert --to python BPIC_2017_event_log_waiting_transformer-suspend.ipynb
python BPIC_2017_event_log_waiting_transformer-suspend.py
rm BPIC_2017_event_log_waiting_transformer-suspend.py
cd ..

