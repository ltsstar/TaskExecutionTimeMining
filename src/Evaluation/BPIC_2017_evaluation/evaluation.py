import datetime
import numpy as np
import collections
import pm4py
from pm4py.objects.petri_net import semantics

from ..evaluation import *


class SampleOutcomes_BPIC2017(SampleOutcomes):
    def __init__(self, case_event_log):
        super().__init__(case_event_log)

    def prepare_event_log(self):
        self.event_log['new_concept'] = self.event_log['concept:name'] +  '__' + self.event_log['EventID'] + '__' + self.event_log['lifecycle:transition']
        self.event_log = self.event_log[self.event_log['concept:name'].str.startswith('W_')]
        #self.event_log = self.event_log.set_index('new_concept')
        self.new_concept_name = 'new_concept'

    def sample_end_time(self, case_log, start_time, net, im):
        get_enabled_tasks = lambda marking : list(semantics.enabled_transitions(net, marking))

        marking = im
        current_time = start_time
        finish_time = dict() 
        activity_count = collections.defaultdict(lambda : collections.defaultdict(int))
        resource_count = collections.defaultdict(lambda : collections.defaultdict(int))
        while get_enabled_tasks(marking):
            pn_task = get_enabled_tasks(marking)[0]
            task, workitem, action = pn_task.label.split('__')
            row = case_log[case_log[self.new_concept_name] == pn_task.label].iloc[0]
            
            seconds_in_day = row['seconds_in_day']
            resource = row['org:resource']
            concept_name = row['concept:name']
            activity_count[action][row['concept:name']] += 1
            resource_count[action][row['org:resource']] += 1
            day_of_week = datetime.datetime.fromtimestamp(current_time).weekday()
        
            #print(action, concept_name, resource)
            
            if action == 'schedule':
                # we assume the schedule -> start transition is instant
                finish_time[task] = current_time
            elif action in ['start', 'resume'] :
                sampled_time = self.sample_start_suspend_time(seconds_in_day = seconds_in_day, resource = resource, concept_name = concept_name,
                                                               resource_count = resource_count[action], activity_count = activity_count[action],
                                                               day_of_week = day_of_week)
                finish_time[task] += sampled_time
            elif action == 'suspend':
                sampled_time =  self.sample_suspend_resume_time(seconds_in_day = seconds_in_day, resource = resource, concept_name = concept_name,
                                                               resource_count = resource_count[action], activity_count = activity_count[action],
                                                               day_of_week = day_of_week)
                finish_time[task] += sampled_time
            else:
                # ['complete', 'ate_abort', 'pi_abort', 'withdraw']
                current_time = max(current_time, finish_time[task])

            marking = semantics.execute(pn_task, net, marking)

        #print('total:', current_time)
        #print('---------')
        return current_time

    def sample_case(self, case_name):
        case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        net, im, fm = pm4py.discover_petri_net_inductive(case_log,
                                                        activity_key='new_concept',
                                                        case_id_key='case:concept:name',
                                                        timestamp_key='time:timestamp')
        start_time = case_log['time:timestamp'].min().timestamp()
        return self.sample_end_time(case_log, start_time, net, im)