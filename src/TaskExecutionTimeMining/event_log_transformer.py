import pandas

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
        start_end_event_log = start_end_event_log[start_end_event_log['duration_seconds'] > 0]
        return start_end_event_log

    def seconds_in_day(event_log,
                    timestamp_name = 'time:timestamp'):
        start_end_event_log = event_log.copy()
        start_end_event_log['seconds_in_day'] = start_end_event_log[timestamp_name].dt.hour * 3600 + \
        start_end_event_log[timestamp_name].dt.minute * 60 + \
        start_end_event_log[timestamp_name].dt.second
        return start_end_event_log
    
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
