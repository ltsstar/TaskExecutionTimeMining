import datetime
import numpy as np
import collections
import pm4py
from pm4py.objects.petri_net import semantics
from pm4py.objects.petri_net import exporter
from evaluation import *


class SampleOutcomes_PCR(SampleOutcomes):
    def __init__(self, event_log,
                 resources=True,
                **kwargs):
        super().__init__(event_log)
        self.resources = resources

    def sample_end_time(self, case_log, start_time):

        finish_times = collections.defaultdict(int)

        current_time = start_time
        current_event = case_log.iloc[0]

        activity_count = collections.defaultdict(int)

        get_seconds_in_day = lambda dt : (dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        get_day_of_week = lambda dt : dt.weekday()

        durations = collections.defaultdict(int)
        for index, current_event in case_log.iterrows():
            event_name = current_event['concept:name']
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
            
            duration = self.sample_duration(seconds_in_day = seconds_in_day,
                                            resource = None,
                                            concept_name = event_name,
                                            resource_count = None,
                                            activity_count = activity_count,
                                            day_of_week = day_of_week
                       )
            finish_times[event_name] = prev_finish_ts + duration
            durations[event_name] = duration
        #finish_time = max(finish_times['timeout'], finish_times['Send notification'], finish_times['Callback timeout'])
        finish_time = max(finish_times.values())
        #print([(key, value-min(filter(lambda v : v>0, finish_times.values()))) for key, value in finish_times.items()])
        #print(durations)
        return finish_time


    def sample_case(self, case_log):
        #case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        start_time = case_log['time:timestamp_start'].min().timestamp()
        return self.sample_end_time(case_log, start_time)