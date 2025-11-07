import numpy
import pandas
import datetime
from collections import Counter, deque, defaultdict
from tqdm.auto import tqdm
from scipy import sparse

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
    
    def start_end_event_log_next(event_log,
                                 merge_activity_on = ['case:concept:name'],
                                 timestamp_name = 'time:timestamp',
                                 start_name_gen = '_start',
                                 complete_name_gen = '_complete',
                                 unique_column = 'id'):
        start_end_event_log = pandas.merge(event_log, event_log,
                                        left_on=merge_activity_on,
                                        right_on=merge_activity_on,
                                        suffixes=(start_name_gen, complete_name_gen),
                                        how='right')
        start_end_event_log.loc[:, 'duration'] = start_end_event_log[timestamp_name + complete_name_gen] - start_end_event_log[timestamp_name + start_name_gen]
        start_end_event_log.loc[:, 'duration_seconds'] = start_end_event_log['duration'] / datetime.timedelta(seconds=1) #(start_end_event_log['duration']).astype('timedelta64[s]').astype(float)
        start_end_event_log.loc[:, 'duration_ms'] = start_end_event_log['duration'] / datetime.timedelta(milliseconds=1)
        start_end_event_log.loc[:, 'duration_hours'] = start_end_event_log['duration'] / datetime.timedelta(hours=1)

        start_end_event_log = start_end_event_log[start_end_event_log[timestamp_name + complete_name_gen] > start_end_event_log[timestamp_name + start_name_gen]]
        ixs = start_end_event_log.groupby(unique_column + start_name_gen)['duration_seconds'].idxmin()
        start_end_event_log = start_end_event_log.loc[ixs]

        return start_end_event_log


    def start_end_event_log_all(event_log,
                            merge_activity_on = ['case:concept:name', 'concept:name'],
                            timestamp_name = 'time:timestamp',
                            lifecycle_col_name = 'lifecycle:transition',
                            start_name_gen = '_start',
                            complete_name_gen = '_complete',
                            unique_column = 'EventID'):
        start_end_event_log = pandas.merge(event_log, event_log,
                                    left_on=merge_activity_on,
                                    right_on=merge_activity_on,
                                    suffixes=(start_name_gen, complete_name_gen))
        
        start_end_event_log.loc[:, 'duration'] = start_end_event_log[timestamp_name + complete_name_gen] - start_end_event_log[timestamp_name + start_name_gen]
        start_end_event_log.loc[:, 'duration_seconds'] = start_end_event_log['duration'] / datetime.timedelta(seconds=1) #(start_end_event_log['duration']).astype('timedelta64[s]').astype(float)
        start_end_event_log.loc[:, 'duration_ms'] = start_end_event_log['duration'] / datetime.timedelta(milliseconds=1)
        start_end_event_log.loc[:, 'duration_hours'] = start_end_event_log['duration'] / datetime.timedelta(hours=1)

        # bad idea: sometimes less than 1 second:
        #start_end_event_log = start_end_event_log[start_end_event_log['duration_seconds'] > 0]
        # better idea:
        start_end_event_log = start_end_event_log[start_end_event_log[timestamp_name + complete_name_gen] > start_end_event_log[timestamp_name + start_name_gen]]
        ixs = start_end_event_log.groupby(unique_column + start_name_gen)['duration_seconds'].idxmin()
        start_end_event_log = start_end_event_log.loc[ixs]


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
        start_end_event_log.loc[:, 'duration_hours'] = start_end_event_log['duration'] / datetime.timedelta(hours=1)

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

    def value_count_per_case_without_lifecycle(event_log,
                     column_name,
                     case_name = 'case:concept:name',
                     timestamp_name = 'time:timestamp',
                     unique_id = 'id'):
        value_count = pandas.merge(event_log, event_log,
                                    left_on=[case_name],
                                    right_on=[case_name],
                                    suffixes=('_first', '_second'))

        value_count = value_count[value_count[timestamp_name + '_first'] >= value_count[timestamp_name + '_second']]

        value_count_gb = value_count.groupby([case_name, timestamp_name + '_first', column_name + '_second']).count()[unique_id + '_first'].reset_index()

        pt = pandas.pivot_table(value_count_gb, index=[case_name, timestamp_name + '_first'],
                                columns=[column_name + '_second'],
                                values= unique_id + '_first', aggfunc='sum',
                                fill_value=0)

        value_count_event_log = pandas.merge(event_log, pt,
                        left_on=[case_name, timestamp_name],
                        right_on=[case_name, timestamp_name + '_first'],
                        how='left',
                        suffixes=('_left', '_right'))
        value_count_event_log = value_count_event_log.fillna(0)

        return value_count_event_log


    '''
    Implements the states the other cases are in when the event occurs
    This was proposed as 'Level 2' for n = 1 and else 'Level 3' encoding in:
        Senderovich, A., Di Francescomarino, C., Ghidini, C., Jorbina, K., & Maggi, F. M. (2017, August).
        Intra and inter-case features in predictive process monitoring: A tale of two dimensions.
        In International Conference on Business Process Management (pp. 306-323).
        Cham: Springer International Publishing.

    '''
    def inter_instance_encoding_last_events(event_log,
                                case_name = 'case:concept:name',
                                timestamp_name = 'time:timestamp',
                                concept_name = 'concept:name',
                                state_prefix = '',
                                n = 1
    ):
        total_events_per_case = event_log.groupby(case_name).size()
        sorted_event_log = event_log.sort_values(timestamp_name, kind='mergesort')
        cols = list(sorted_event_log.columns)
        case_name_idx = cols.index(case_name)
        concept_name_idx = cols.index(concept_name)

        # Count unique states
        unique_states = set()
        case_to_history = {}
        processed = defaultdict(int)

        for row in tqdm(sorted_event_log.itertuples(index=False), total=sorted_event_log.shape[0], desc='Counting unique states'):
            case_id = row[case_name_idx]
            event_label = row[concept_name_idx]

            if case_id not in case_to_history:
                case_to_history[case_id] = deque(maxlen=n)

            history = case_to_history[case_id]
            history.append(event_label)
            state = tuple(history)
            unique_states.add(state)

            processed[case_id] += 1
            if processed[case_id] == total_events_per_case[case_id]:
                del case_to_history[case_id]
            

        unique_states = sorted(list(unique_states))
        # Map states to ids and column names
        state_to_id = {state: i for i, state in enumerate(unique_states)}
        col_names = [state_prefix + '_'.join(state) for state in unique_states]
        num_states = len(unique_states)

        # Create column names from states
        state_to_col = {state : state_prefix + '_'.join(state) for state in sorted(unique_states)}

        # --
        # Second: Compute counts
        # --
        #values = numpy.empty((len(sorted_event_log), num_states), dtype=int)
        values_sparse = sparse.lil_matrix((len(sorted_event_log), num_states), dtype='int16')

        count_array = numpy.zeros(num_states, dtype=int)
        case_to_history = {}
        case_to_state_id = {}
        processed = defaultdict(int)
        ids_array = numpy.arange(num_states)

        for row_num, row in enumerate(tqdm(sorted_event_log.itertuples(index=False), total=sorted_event_log.shape[0], desc='Computing state counts')):
            case_id = row[case_name_idx]
            event_label = row[concept_name_idx]
    
            if case_id not in case_to_history:
                case_to_history[case_id] = deque(maxlen=n)
                case_to_state_id[case_id] = -1
            
            history = case_to_history[case_id]

            # Update state if case already has a state
            old_id = case_to_state_id[case_id]
            if old_id != -1:
                count_array[old_id] -= 1
            
            # Append new activity and get new state
            history.append(event_label)
            new_state = tuple(history)
            new_id = state_to_id[new_state]
            count_array[new_id] += 1
            case_to_state_id[case_id] = new_id
            
            # Compute row counts: count_array - 1 if id == new_id
            subtract = (ids_array == new_id).astype(int)
            row_counts = count_array - subtract
            #values[row_num] = row_counts
            values_sparse[row_num, :] = row_counts
            
            # Increment processed
            processed[case_id] += 1
            
            # If this is the last event for the case, remove it from counts immediately
            if processed[case_id] == total_events_per_case[case_id]:
                count_array[new_id] -= 1
                del case_to_history[case_id]
                del case_to_state_id[case_id]

        # Create new columns dataframe
        #new_cols_df = pandas.DataFrame(values, columns=col_names, index=sorted_event_log.index)
        new_cols_df = pandas.DataFrame.sparse.from_spmatrix(values_sparse, columns=col_names, index=sorted_event_log.index)
        # Concat to sorted_df
        sorted_event_log = pandas.concat([sorted_event_log, new_cols_df], axis=1)

        result_event_log = sorted_event_log.sort_index()
        return result_event_log
