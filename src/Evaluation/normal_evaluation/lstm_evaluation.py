import pandas as pd
from normal_evaluation.normal_evaluation import *

class SampleOutcomes_LSTM(SampleOutcomes_Normal):
    def __init__(self, lstm_model,
                max_sample=10, **kwargs):
        super().__init__(**kwargs)
        self.lstm_model = lstm_model
        self.max_sample = max_sample


    def sample_end_time(self, case_log, start_time):
        #get_enabled_tasks = lambda marking : list(semantics.enabled_transitions(net, marking))

        #marking = im
        current_time = start_time
        finish_time = dict()
        
        events = []

        for index, current_event in case_log.iterrows():
            current_event_dict = current_event.to_dict()

            # inter instance encoding
            ii_columns = {}
            if self.inter_instance_encoding:
                for col in self.inter_instance_column_names:
                    if col in current_event:
                        ii_columns[col] = current_event[col]
                    else:
                        ii_columns[col] = 0


            # it can happen that unrealistically high values get sampled
            # this causes problems with the conversion to datetime
            # therefore return
            if current_time > datetime.datetime(3000, 1, 1).timestamp():
                return current_time

            # feature engineering
            current_time_ts = datetime.datetime.fromtimestamp(current_time)
            seconds_in_day = (current_time_ts - current_time_ts.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            day_of_week = datetime.datetime.fromtimestamp(current_time).weekday()   

            current_event_dict['seconds_in_day'] = seconds_in_day
            current_event_dict['day_in_week'] = day_of_week

            events.append(current_event_dict)    

            finish_time = self.sample_duration(events)
            current_time += finish_time

        return current_time
    
    def sample_duration(self, event_list):
        sampled_mean, sampled_variance = self.lstm_model.predict(event_list)

        for i in range(self.max_sample):
            sampled_time = np.random.normal(sampled_mean, sampled_variance)
            if sampled_time > 0:
                break
        if sampled_time < 0:
            #print('warning sample time below 0:', sampled_time, concept_name)
            return 0
        else:
            return sampled_time