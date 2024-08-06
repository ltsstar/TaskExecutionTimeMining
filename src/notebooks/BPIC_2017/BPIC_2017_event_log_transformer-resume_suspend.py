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
                                                                   complete_name_1 = 'complete', complete_name_2 = 'ate_abort')


# In[9]:


start_end_event_log.groupby(['lifecycle:transition_start', 'lifecycle:transition_complete']).count()


# In[10]:


(start_end_event_log['duration_seconds']/3600).describe()


# In[11]:


(start_end_event_log['duration_seconds']/3600).plot.box()


# In[12]:


start_end_event_log[start_end_event_log['duration_seconds'] > 3000*3600]


# In[13]:


start_end_event_log[start_end_event_log['case:concept:name'] == 'Application_1283264254'].sort_values('time:timestamp_start')


# In[14]:


event_log[event_log['case:concept:name'] == 'Application_1283264254'].sort_values('time:timestamp')


# In[15]:


# Seconds in day
start_end_event_log = TransformEventLog.seconds_in_day(start_end_event_log, 'time:timestamp_start')


# In[16]:


start_end_event_log


# In[17]:


#start_end_event_log[(start_end_event_log['case:concept:name'] == 'Application_949646433')].sort_values('time:timestamp_start')\
#[['case:concept:name', 'concept:name', 'org:resource_start', 'lifecycle:transition_start', 'time:timestamp_start', 'org:resource_complete', 'lifecycle:transition_complete', 'time:timestamp_complete', 'duration_seconds']]


# In[18]:


# Resource counts

resource_count_event_log = TransformEventLog.value_count_per_case(start_end_event_log, 'org:resource_start',
                                                                  timestamp_name = 'time:timestamp_start',
                                                                 lifecycle_col_name = 'lifecycle:transition_start')


# In[19]:


resource_count_event_log


# In[20]:


activity_count_event_log = TransformEventLog.value_count_per_case(resource_count_event_log, 'concept:name',
                                                                  timestamp_name = 'time:timestamp_start',
                                                                 lifecycle_col_name = 'lifecycle:transition_start' )


# In[21]:


activity_count_event_log


# In[22]:


activity_count_event_log.to_csv('../transformed_event_logs/BPIC_2017_resume_suspend.csv', index=False, date_format='%Y-%m-%d %H:%M:%S.%f')
activity_count_event_log.to_pickle('../transformed_event_logs/BPIC_2017_resume_suspend.pickle')

