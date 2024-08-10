import pandas
import datetime

class TransformEventLog:
    def start_end_event_log(event_log,
                            merge_activity_on = ['case:concept:name', 'org:resource', 'concept:name'],
                            timestamp_name = 'time:timestamp',
                            lifecycle_col_name = 'lifecycle:transition',
                            start_name = 'START',
                            complete_name = 'COMPLETE'):
        merged_event_log = pandas.merge(event_log, event_log,
                                    left_on=merge_activity_on,
                                    right_on=merge_activity_on,
                                    suffixes=('_start', '_complete'))
        start_end_event_log = merged_event_log[(merged_event_log[lifecycle_col_name + '_start'] == start_name) & (merged_event_log[lifecycle_col_name + '_complete'] == complete_name)]
        start_end_event_log.loc[:, 'duration'] = start_end_event_log[timestamp_name + '_complete'] - start_end_event_log[timestamp_name + '_start']
        start_end_event_log.loc[:, 'duration_seconds'] =  (start_end_event_log['duration']).astype('timedelta64[s]').astype(int)
        #start_end_event_log = start_end_event_log[start_end_event_log['duration_seconds'] > 0]
        return start_end_event_log

    def start_end_event_log_mult(event_log,
                            merge_activity_on = ['case:concept:name', 'concept:name'],
                            timestamp_name = 'time:timestamp',
                            lifecycle_col_name = 'lifecycle:transition',
                            start_name_1 = 'START',
                            start_name_2 = 'START',
                            start_name_3 = 'START',
                            complete_name_1 = 'COMPLETE',
                            complete_name_2 = 'COMPLETE',
                            complete_name_3 = 'COMPLETE',
                            start_name_gen = '_start',
                            complete_name_gen = '_complete',
                            unique_column = 'EventID'):
        merged_event_log = pandas.merge(event_log, event_log,
                                    left_on=merge_activity_on,
                                    right_on=merge_activity_on,
                                    suffixes=(start_name_gen, complete_name_gen))
        start_end_event_log = merged_event_log[
            ((merged_event_log[lifecycle_col_name + start_name_gen] == start_name_1) | (merged_event_log[lifecycle_col_name + start_name_gen] == start_name_2) \
                 | (merged_event_log[lifecycle_col_name + start_name_gen] == start_name_3)) & \
            ((merged_event_log[lifecycle_col_name + complete_name_gen] == complete_name_1) | (merged_event_log[lifecycle_col_name + complete_name_gen] == complete_name_2)
                 |  (merged_event_log[lifecycle_col_name + complete_name_gen] == complete_name_3))
        ]
        start_end_event_log.loc[:, 'duration'] = start_end_event_log[timestamp_name + complete_name_gen] - start_end_event_log[timestamp_name + start_name_gen]
        start_end_event_log.loc[:, 'duration_seconds'] = start_end_event_log['duration'] / datetime.timedelta(seconds=1) #(start_end_event_log['duration']).astype('timedelta64[s]').astype(float)
        start_end_event_log.loc[:, 'duration_ms'] = start_end_event_log['duration'] / datetime.timedelta(milliseconds=1)
        start_end_event_log.loc[:, 'duration_hours'] = start_end_event_log['duration'] / datetime.time(hours=1)

        # bad idea: sometimes less than 1 second:
        #start_end_event_log = start_end_event_log[start_end_event_log['duration_seconds'] > 0]
        # better idea:
        start_end_event_log = start_end_event_log[start_end_event_log[timestamp_name + complete_name_gen] > start_end_event_log[timestamp_name + start_name_gen]]
        ixs = start_end_event_log.groupby(unique_column + start_name_gen)['duration_seconds'].idxmin()
        start_end_event_log = start_end_event_log.loc[ixs]


        return start_end_event_log
    
    def case_duration_event_log(event_log,
                                first_timestamp,
                                second_timestamp,
                                out_column_name='case_duration'):
        merged_event_log = pandas.merge(event_log,
                                        event_log[['case:concept:name', first_timestamp]],
                                        left_on=['case:concept:name'],
                                        right_on=['case:concept:name'],
                                        suffixes=('', '_case_start'))

        start_case_event_log = merged_event_log.loc[merged_event_log.groupby(['case:concept:name', 'concept:name'])[first_timestamp + '_case_start'].idxmin()]

        merged_event_log = pandas.merge(start_case_event_log,
                                        start_case_event_log[['case:concept:name', second_timestamp]],
                                        left_on=['case:concept:name'],
                                        right_on=['case:concept:name'],
                                        suffixes=('', '_case_end'))

        start_end_case_event_log = merged_event_log.loc[
            merged_event_log.groupby(['case:concept:name', 'concept:name'])[second_timestamp + '_case_end'].idxmax()
        ]
        case_duration_log = start_end_case_event_log.copy()
        case_duration_log[out_column_name] = case_duration_log[second_timestamp + '_case_end'] - case_duration_log[first_timestamp + '_case_start']
        case_duration_log[out_column_name + '_seconds'] = (case_duration_log[out_column_name]).astype('timedelta64[s]').astype(int)

        case_duration_log = case_duration_log.loc[case_duration_log.groupby('case:concept:name')['concept:name'].idxmin()]

        case_duration_log = case_duration_log[['case:concept:name', first_timestamp + '_case_start', second_timestamp + '_case_end',
                                            out_column_name, out_column_name + '_seconds']]
        
        return case_duration_log
    
    def case_duration_event_log_2(event_log,
                                  activity_duration_col_name,
                                  out_col_name='case_duration'):
        return event_log.groupby(['case:concept:name'])[activity_duration_col_name + '_seconds'].sum().to_frame().rename(columns={activity_duration_col_name : out_col_name })

    def seconds_in_day(event_log,
                    timestamp_name = 'time:timestamp'):
        start_end_event_log = event_log.copy()
        start_end_event_log['seconds_in_day'] = start_end_event_log[timestamp_name].dt.hour * 3600 + \
        start_end_event_log[timestamp_name].dt.minute * 60 + \
        start_end_event_log[timestamp_name].dt.second
        return start_end_event_log
    
    def day_of_week(event_log,
                    timestamp_name = 'time:timestamp',
                    out_col_name = 'day_of_week'):
        event_log[out_col_name] = event_log[timestamp_name].dt.weekday
        return event_log
        
    
    def value_count_per_case(event_log,
                     column_name,
                     case_name = 'case:concept:name',
                     concept_name = 'concept:name',
                     timestamp_name = 'time:timestamp',
                     lifecycle_col_name = 'lifecycle:transition'):
        value_count = pandas.merge(event_log, event_log,
                                    left_on=[case_name],
                                    right_on=[case_name],
                                    suffixes=('_first', '_second'))

        value_count = value_count[value_count[timestamp_name + '_first'] >= value_count[timestamp_name + '_second']]

        value_count_gb = value_count.groupby([case_name, concept_name + '_first',
                                                timestamp_name + '_first', column_name + '_second']).count()[lifecycle_col_name + '_first'].reset_index()

        pt = pandas.pivot_table(value_count_gb, index=[case_name, concept_name + '_first', timestamp_name + '_first'],
                                columns=[column_name + '_second'],
                                values= lifecycle_col_name + '_first', aggfunc='sum',
                                fill_value=0)

        value_count_event_log = pandas.merge(event_log, pt,
                        left_on=[case_name, concept_name, timestamp_name],
                        right_on=[case_name, concept_name + '_first', timestamp_name + '_first'],
                        how='left',
                        suffixes=('_left', '_right'))
        value_count_event_log = value_count_event_log.fillna(0)

        return value_count_event_log
