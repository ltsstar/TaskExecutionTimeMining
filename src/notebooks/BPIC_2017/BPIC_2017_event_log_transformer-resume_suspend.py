#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pm4py
import sys
sys.path.append('../../TaskExecutionTimeMining/')
from event_log_transformer import *
pandas.set_option('display.max_columns', None)
pandas.set_option('display.max_rows', 200)


# In[2]:


file_path = '../../../data/BPI Challenge 2017.xes'
event_log = pm4py.read_xes(file_path)


# In[3]:


event_log


# In[4]:


#event_log['concept'] = event_log['concept:name'] + '_' + event_log['lifecycle:transition']
#event_log = event_log[event_log['concept:name'].str.startswith('W_')]


# In[5]:


#event_log[:99999].to_csv('test.csv', index=False, date_format='%Y-%m-%d %H:%M:%S.%f')


# In[6]:


event_log['lifecycle:transition'].unique()


# In[7]:


event_log['concept:name'].unique()


# In[8]:


start_end_event_log = TransformEventLog.start_end_event_log_mult(event_log,
                                                                   start_name_1 = 'start',
                                                                   start_name_2 = 'resume',
                                                                 
                                                                   complete_name_3 = 'suspend',
                                                                   complete_name_1 = 'complete',
                                                                   complete_name_2 = 'ate_abort'
                                                                )


# In[9]:


start_end_event_log.groupby(['lifecycle:transition_start', 'lifecycle:transition_complete']).count()


# In[10]:


(start_end_event_log['duration_seconds']).describe()


# In[11]:


(start_end_event_log['duration_seconds']).plot.box()


# In[12]:


start_end_event_log[start_end_event_log['case:concept:name'] == 'Application_1283264254'].sort_values('time:timestamp_start')


# In[13]:


# remove cases with overlapping activities

overlapping_count = 0
for case_id in start_end_event_log['case:concept:name'].unique():
    selected_log = start_end_event_log[start_end_event_log['case:concept:name'] == case_id].sort_values('time:timestamp_start')
    selected_log['interval'] = pandas.IntervalIndex.from_arrays(selected_log['time:timestamp_start'], selected_log['time:timestamp_complete'])
    
    activities = list(selected_log['concept:name'])
    #print(activities)
    case = []
    print_case = False
    do_not_process = []
    for index, row in selected_log.iterrows():
        if index in do_not_process:
            continue
        #print(row['concept:name'], activities)
        interlapping = [row['concept:name']]
        activities.remove(row['concept:name'])
        for index_2, row_2 in selected_log.loc[index:].iterrows():
            if index == index_2:
                continue
            if row['interval'].overlaps(row_2['interval']):
                activities.remove(row_2['concept:name'])
                interlapping.append(row_2['concept:name'])
                do_not_process.append(index_2)
                if row['concept:name'] != row_2['concept:name']: #and \
                    #(row_2['concept:name'] == 'W_Shortened completion ' or row['concept:name'] == 'W_Shortened completion '):
                    print_case = True
        case.append(interlapping)
    if print_case:
        overlapping_count += 1
        print(case_id)
        print(case)
        start_end_event_log = start_end_event_log[~(start_end_event_log['case:concept:name'] == case_id)]
print(overlapping_count)


# In[14]:


start_end_event_log[start_end_event_log['concept:name'] == 'W_Shortened completion '].shape


# In[15]:


print(case_id)


# In[16]:


start_end_event_log['case:concept:name'].nunique()


# In[17]:


start_end_event_log[start_end_event_log['case:concept:name'] == 'Application_912911968'].sort_values('time:timestamp_start')


# In[18]:


start_end_event_log[start_end_event_log['case:concept:name'] == 'Application_912911968'].sort_values('time:timestamp_start')\
[['org:resource_start', 	'concept:name', 'lifecycle:transition_start', 'time:timestamp_start', 'time:timestamp_complete']]


# In[19]:


event_log[event_log['case:concept:name'] == 'Application_912911968'].sort_values('time:timestamp')


# In[20]:


# Seconds in day
start_end_event_log = TransformEventLog.seconds_in_day(start_end_event_log, 'time:timestamp_start')
# day of week
start_end_event_log = TransformEventLog.day_of_week(start_end_event_log, 'time:timestamp_start')


# In[21]:


start_end_event_log


# In[22]:


#start_end_event_log[(start_end_event_log['case:concept:name'] == 'Application_949646433')].sort_values('time:timestamp_start')\
#[['case:concept:name', 'concept:name', 'org:resource_start', 'lifecycle:transition_start', 'time:timestamp_start', 'org:resource_complete', 'lifecycle:transition_complete', 'time:timestamp_complete', 'duration_seconds']]


# In[23]:


# Resource counts

resource_count_event_log = TransformEventLog.value_count_per_case(start_end_event_log, 'org:resource_start',
                                                                  timestamp_name = 'time:timestamp_start',
                                                                 lifecycle_col_name = 'lifecycle:transition_start')


# In[24]:


resource_count_event_log


# In[ ]:


activity_count_event_log = TransformEventLog.value_count_per_case(resource_count_event_log, 'concept:name',
                                                                  timestamp_name = 'time:timestamp_start',
                                                                 lifecycle_col_name = 'lifecycle:transition_start' )


# In[ ]:


activity_count_event_log


# In[ ]:


activity_count_event_log.to_csv('../transformed_event_logs/BPIC_2017_resume_suspend.csv', index=False, date_format='%Y-%m-%d %H:%M:%S.%f')
activity_count_event_log.to_pickle('../transformed_event_logs/BPIC_2017_resume_suspend.pickle')

