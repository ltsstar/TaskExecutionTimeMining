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
        
        case_log_sim = case_log.sort_values(self.timestamp_key).copy().reset_index(drop=True)
        if 'seconds_in_day' not in case_log_sim.columns:
            case_log_sim['seconds_in_day'] = float('nan')
        case_log_sim['seconds_in_day'] = case_log_sim['seconds_in_day'].astype('float64', copy=False)
        if 'day_in_week' not in case_log_sim.columns:
            case_log_sim['day_in_week'] = float('nan')
        case_log_sim['day_in_week'] = case_log_sim['day_in_week'].astype('float64', copy=False)

        for row_idx, current_event in case_log_sim.iterrows():

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

            case_log_sim.at[row_idx, 'seconds_in_day'] = seconds_in_day
            case_log_sim.at[row_idx, 'day_in_week'] = day_of_week

            prefix_df = case_log_sim.iloc[:row_idx + 1]
            #prefix_df = case_log_sim[:row_idx + 1]
            finish_time = self.sample_duration(prefix_df)
            current_time += finish_time

        return current_time
    
    def sample_duration(self, prefix_df):
        sampled_mean, sampled_variance = self.lstm_model.predict(prefix_df)

        for i in range(self.max_sample):
            sampled_time = np.random.normal(sampled_mean, sampled_variance)
            if sampled_time > 0:
                break
        if sampled_time < 0:
            #print('warning sample time below 0:', sampled_time, concept_name)
            return 0
        else:
            return sampled_time