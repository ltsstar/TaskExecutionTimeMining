import datetime
import numpy as np
import collections
import pm4py
from pm4py.objects.petri_net import semantics

from evaluation import *


class SampleOutcomes_Normal(SampleOutcomes):
    def __init__(self, event_log, resources=True,
                    activity_key='concept:name_start',
                    case_id_key='case:concept:name',
                    resource_key='org:resource_start',
                    timestamp_key='time:timestamp_start',
                    value_key=None,
                **kwargs):
        super().__init__(event_log)
        self.resources = resources
        self.activity_key = activity_key
        self.case_id_key = case_id_key
        self.resource_key = resource_key
        self.timestamp_key = timestamp_key
        self.value_key = value_key

    def sample_end_time(self, case_log, start_time):
        #get_enabled_tasks = lambda marking : list(semantics.enabled_transitions(net, marking))

        #marking = im
        current_time = start_time
        finish_time = dict()

        # feature encoding
        activity_count = collections.defaultdict(int)
        resource_count = collections.defaultdict(int)

        for index, current_event in case_log.iterrows():
            #pn_task = get_enabled_tasks(marking)[0]
            #row = case_log[case_log[self.activity_key] == task].iloc[0]

            if self.value_key:
                value = current_event[self.value_key]
            else:
                value = None
            
            seconds_in_day = current_event['seconds_in_day']
            if self.resources:
                resource = current_event[self.resource_key]
            else:
                resource = None
            concept_name = current_event[self.activity_key]

            # feature encoding : aggregation encoding
            activity_count[current_event[self.activity_key]] += 1
            if self.resources:
                resource_count[current_event[self.resource_key]] += 1
            else:
                resource_count = None

            # it can happen that unrealistically high values get sampled
            # this causes problems with the conversion to datetime
            # therefore return
            if current_time > datetime.datetime(3000, 1, 1).timestamp():
                return current_time

            # feature engineering
            current_time_ts = datetime.datetime.fromtimestamp(current_time)
            seconds_in_day = (current_time_ts - current_time_ts.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            day_of_week = datetime.datetime.fromtimestamp(current_time).weekday()
                       
            finish_time = self.sample_duration(seconds_in_day = seconds_in_day,
                                               resource = resource,
                                               concept_name = concept_name,
                                               resource_count = resource_count,
                                               activity_count = activity_count,
                                               day_of_week = day_of_week,
                                               value = value
                                              )
            
            current_time += finish_time
            #marking = semantics.execute(pn_task, net, marking)

        #print('total:', current_time)
        #print('---------')
        return current_time


    def sample_case(self, case_log):
        #case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        #net, im, fm = pm4py.discover_petri_net_inductive(case_log,
        #                                                activity_key=self.activity_key,
        #                                                case_id_key=self.case_id_key,
        #                                                timestamp_key=self.timestamp_key)
        start_time = case_log[self.timestamp_key].min().timestamp()
        return self.sample_end_time(case_log, start_time)