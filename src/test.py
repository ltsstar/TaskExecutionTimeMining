import pm4py
from TaskExecutionTimeMining.DecisionTree import *


def load_event_log(path):
    event_log = pm4py.read_xes(file_path)
    merged_event_log = pandas.merge(event_log, event_log,
                                    left_on=['case:concept:name', 'org:resource', 'concept:name'],
                                    right_on=['case:concept:name', 'org:resource', 'concept:name'],
                                    suffixes=('_start', '_complete'))
    start_end_event_log = merged_event_log[(merged_event_log['lifecycle:transition_start'] == 'START') & (merged_event_log['lifecycle:transition_complete'] == 'COMPLETE')]
    start_end_event_log.loc[:, 'duration'] = start_end_event_log['time:timestamp_complete'] - start_end_event_log['time:timestamp_start']
    start_end_event_log.loc[:, 'duration_seconds'] =  (start_end_event_log['duration']).astype('timedelta64[s]').astype(int)
    start_end_event_log = start_end_event_log[start_end_event_log['duration_seconds'] > 0]
    return start_end_event_log


file_path = '../data/BPI_Challenge_2012.xes'
start_end_event_log = load_event_log(file_path)


relevant_log = start_end_event_log[['org:resource', 'concept:name', 'case:AMOUNT_REQ_start', 'duration_seconds']]
dt = DecisionTree()
res = dt.fit(relevant_log)
print(res)