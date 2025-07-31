import datetime
import collections
from functools import partial
import numpy as np
import os
import pickle
from drbart_parser import *

from evaluation import *


class SampleOutcomesAdvanced(SampleOutcomes):
    def __init__(self,
                 drbart_model_path,
                 categorical_args,
                 continuous_args,
                 known_activities,
                 known_resources,
                 resources=True,
                 max_sample=10,
                 max_sample_value = 3600*24*365, #a year
                 timestamp_key='time:timestamp_start',
                 resource_key='org:resource',
                 activity_key='concept:name',
                 strict_parsing=True,
                 **kwargs):
        super().__init__()
        self.drbart_models = self.load_drbart_models(drbart_model_path, strict_parsing)
        self.transformations = self.load_transformations(drbart_model_path)
        self.splitting_column, assignments, self.routing_rules = self.load_gate(drbart_model_path)
        self.unique_ids = np.unique(assignments)
        self.max_sample = max_sample
        self.max_sample_value = max_sample_value
        self.timestamp_key = timestamp_key
        self.categorical_args = categorical_args
        self.continuous_args = continuous_args
        self.known_activities = known_activities
        self.known_resources = known_resources
        self.value_key = False
        self.resources = resources
        self.resource_key = resource_key
        self.activity_key = activity_key


    def load_drbart_models(self, drbart_model_path, strict_parsing):
        model_names = [name for name in os.listdir(drbart_model_path) if os.path.isdir(os.path.join(drbart_model_path, name))]
        return {model_name : DRBART(parser_dir = drbart_model_path + model_name + '/', strict_parser=strict_parsing) for model_name in model_names}
    
    def load_transformations(self, drbart_model_path):
        with open(drbart_model_path + 'transformations.pickle', 'rb') as f:
            data = pickle.load(f)
        return data
    
    def load_gate(self, drbart_model_path):
        with open(drbart_model_path + 'gate.pickle', 'rb') as f:
            data = pickle.load(f)
        return data[0], data[1], data[2]
    
    def transform_current_event(self, event):
        for transformation_column, (m, v) in self.transformations.items():
            event[transformation_column] = np.log1p(event[transformation_column])
            event[transformation_column] = (event[transformation_column] - m) / v
        return event

    def reverse_transform_duration(self, duration, key='duration_seconds'):
        m, v = self.transformations[key]
        return np.expm1(duration * v + m)

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

            transformed_current_event = self.transform_current_event(current_event)

            if self.value_key:
                value = transformed_current_event[self.value_key]
            else:
                value = None
            
            seconds_in_day = transformed_current_event['seconds_in_day']
            if self.resources:
                resource = transformed_current_event[self.resource_key]
            else:
                resource = None
            concept_name = transformed_current_event[self.activity_key]

            # feature encoding : aggregation encoding
            activity_count[transformed_current_event[self.activity_key]] += 1
            if self.resources:
                resource_count[transformed_current_event[self.resource_key]] += 1
            else:
                resource_count = None

            # feature engineering
            current_time_ts = datetime.datetime.fromtimestamp(current_time)
            seconds_in_day = (current_time_ts - current_time_ts.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            day_of_week = datetime.datetime.fromtimestamp(current_time).weekday()

            drbart_model_id = self.identify_drbart_model(transformed_current_event)
            drbart_model = self.drbart_models[str(drbart_model_id)]
            for i in range(self.max_sample):
                try:
                    duration = self.sample_duration(drbart_model = drbart_model,
                                                    seconds_in_day = seconds_in_day,
                                                    resource = resource,
                                                    concept_name = concept_name,
                                                    resource_count = resource_count,
                                                    activity_count = activity_count,
                                                    day_of_week = day_of_week,
                                                    value = value
                                                    )
                    real_finish_time = self.reverse_transform_duration(duration)
                except Exception as e:
                    print('Case sampling error:', dict(current_event))
                    real_finish_time = 0.0

                if real_finish_time < self.max_sample_value:
                    break
            if real_finish_time >= self.max_sample_value:
                print('sampled duration is still above limit!')
                real_finish_time = self.max_sample_value
            current_time += real_finish_time
            #marking = semantics.execute(pn_task, net, marking)

        #print('total:', current_time)
        #print('---------')
        return current_time
    
    def identify_drbart_model(self, current_event):
        value = current_event[self.splitting_column]
        range_routing = isinstance(self.routing_rules[0], tuple) or (isinstance(self.routing_rules[0], list) and isinstance(self.routing_rules[0][0], tuple))
        model_id = None
        if range_routing:
            min_interval, max_interval = float('inf'), float('-inf')
            for i, rule_list in zip(self.unique_ids, self.routing_rules):
                if isinstance(rule_list, tuple):
                    rules = [rule_list]
                else:
                    rules = rule_list
                for rule in rules:
                    #update min-max intervals (might be avoidable since KBinsDiscretizer uses 0 for the min interval and n-1 for the highest one (?))
                    if min_interval > rule[0]:
                        min_interval = rule[0]
                        min_interval_i = i
                    if max_interval < rule[1]:
                        max_interval = rule[1]
                        max_interval_i = i
                    # check if value is in interval : KBinsDiscretizer uses left-open, right-closed intervals, so:
                    # a <= x < b
                    if rule[0] <= value < rule[1]:
                        model_id = i
                        break
            if model_id is None:
                if min_interval >= value:
                    model_id = min_interval_i
                if max_interval <= value:
                    model_id = max_interval_i
        else:
            for i, rule_list in zip(self.unique_ids, self.routing_rules):
                if not isinstance(rule_list, list):
                    rules = [rule_list]
                else:
                    rules = rule_list
                for rule in rules:
                    if rule == value:
                        model_id = i
                        break
            if model_id is None:
                #print('warning: split not known')
                model_id = np.random.choice(self.unique_ids)
        if model_id is None:
            print('model id is None', value, min_interval, max_interval)
        return model_id

    def sample_duration(self, drbart_model, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week,
                        value):

        '''
        The eval() function calls the parameters passed
        '''
        continuous_variables = list()
        for cv in self.continuous_args:
            continuous_variables.append(eval(cv))
        categorical_variables = list()
        for cv in self.categorical_args:
            r = eval(cv)
            if type(r) is list:
                categorical_variables += r
            else:
                categorical_variables.append(r)

        
        pf = partial(drbart_model.sample,
                                    categorical_variables,
                                    continuous_variables
                    )
        sample_time = lambda : pf()[1][0]
        return sample_time()
    
    def sample_case(self, case_log):
        #case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        #net, im, fm = pm4py.discover_petri_net_inductive(case_log,
        #                                                activity_key=self.activity_key,
        #                                                case_id_key=self.case_id_key,
        #                                                timestamp_key=self.timestamp_key)
        start_time = case_log[self.timestamp_key].min().timestamp()
        return self.sample_end_time(case_log, start_time)
    

class SampleOutcomesAdvancedPCR(SampleOutcomesAdvanced):
    def __init__(self,
                 drbart_model_path,
                 categorical_args,
                 continuous_args,
                 known_activities,
                 resources=True,
                 max_sample=10,
                 max_sample_value=3600*24*365, #a year
                 timestamp_key='time:timestamp_start',
                 **kwargs):
        super().__init__(drbart_model_path, categorical_args, continuous_args, known_activities,
                         [], resources, max_sample, max_sample_value, timestamp_key, **kwargs)

    def sample_end_time(self, case_log, start_time):

        finish_times = collections.defaultdict(int)

        current_time = start_time
        current_event = case_log.iloc[0]

        activity_count = collections.defaultdict(int)

        get_seconds_in_day = lambda dt : (dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        get_day_of_week = lambda dt : dt.weekday()

        durations = collections.defaultdict(int)
        for index, current_event in case_log.iterrows():
            transformed_current_event = self.transform_current_event(current_event)

            event_name = transformed_current_event['concept:name']
            if event_name in ['Match patient data', 'Wait for plate validation', 'timeout']:
                prev_finish_ts = start_time
            elif event_name == 'Receive sample state':
                prev_finish_ts = finish_times['Wait for plate validation']
            elif event_name in ['Export to EMS', 'Export result']:
                prev_finish_ts = max(finish_times['Receive sample state'], finish_times['Match patient data'])
            elif event_name == 'Callback timeout':
                prev_finish_ts = max(finish_times['Export to EMS'], finish_times['Export result'],
                                     finish_times['Receive sample state'], finish_times['Match patient data'])
            elif event_name == 'Send notification':
                prev_finish_ts = finish_times['timeout']

            prev_finish_dt = datetime.datetime.fromtimestamp(prev_finish_ts)
            seconds_in_day = get_seconds_in_day(prev_finish_dt)
            day_of_week = prev_finish_dt.weekday()
            activity_count[event_name] += 1
            
            drbart_model_id = self.identify_drbart_model(transformed_current_event)
            drbart_model = self.drbart_models[str(drbart_model_id)]
            for i in range(self.max_sample):
                duration = self.sample_duration(drbart_model = drbart_model,
                                                seconds_in_day = seconds_in_day,
                                                resource = None,
                                                concept_name = event_name,
                                                resource_count = None,
                                                activity_count = activity_count,
                                                day_of_week = day_of_week,
                                                value = None
                        )
                real_finish_time = self.reverse_transform_duration(duration)
                if real_finish_time < self.max_sample_value:
                    break
            if real_finish_time >= self.max_sample_value:
                print('sampled duration is still above limit!')
            finish_times[event_name] = prev_finish_ts + real_finish_time
            durations[event_name] = real_finish_time
        #finish_time = max(finish_times['timeout'], finish_times['Send notification'], finish_times['Callback timeout'])
        finish_time = max(finish_times.values())
        #print([(key, value-min(filter(lambda v : v>0, finish_times.values()))) for key, value in finish_times.items()])
        #print(durations)
        return finish_time