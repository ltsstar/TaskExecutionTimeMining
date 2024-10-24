import datetime
import numpy as np
import collections
import pm4py
from pm4py.objects.petri_net import semantics

from evaluation import *


class SampleOutcomes_Normal(SampleOutcomes):
    def __init__(self, event_log, resources=True):
        super().__init__(event_log)
        self.resources = resources

    def sample_end_time(self, case_log, start_time, net, im):
        get_enabled_tasks = lambda marking : list(semantics.enabled_transitions(net, marking))

        marking = im
        current_time = start_time
        finish_time = dict()

        # feature encoding
        activity_count = collections.defaultdict(int)
        resource_count = collections.defaultdict(int)

        while get_enabled_tasks(marking):
            pn_task = get_enabled_tasks(marking)[0]
            task = pn_task.label
            row = case_log[case_log['concept:name'] == task].iloc[0]
            
            seconds_in_day = row['seconds_in_day']
            if self.resources:
                resource = row['org:resource']
            else:
                resource = None
            concept_name = row['concept:name']

            # feature encoding : aggregation encoding
            activity_count[row['concept:name']] += 1
            if self.resources:
                resource_count[row['org:resource']] += 1
            else:
                resource_count = None

            # feature engineering
            current_time_ts = datetime.datetime.fromtimestamp(current_time)
            seconds_in_day = (current_time_ts - current_time_ts.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            day_of_week = datetime.datetime.fromtimestamp(current_time).weekday()
            
            print(concept_name, seconds_in_day)
           
            finish_time = self.sample_duration(seconds_in_day = seconds_in_day,
                                               resource = resource,
                                               concept_name = concept_name,
                                               resource_count = resource_count,
                                               activity_count = activity_count,
                                               day_of_week = day_of_week
                                              )
            print(task, finish_time)
            current_time += finish_time
            marking = semantics.execute(pn_task, net, marking)

        #print('total:', current_time)
        #print('---------')
        return current_time


    def sample_case(self, case_name):
        case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        net, im, fm = pm4py.discover_petri_net_inductive(case_log,
                                                        activity_key='concept:name',
                                                        case_id_key='case:concept:name',
                                                        timestamp_key='time:timestamp')
        start_time = case_log['time:timestamp'].min().timestamp()
        return self.sample_end_time(case_log, start_time, net, im)