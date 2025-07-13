import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm.notebook import tqdm


from mutual_information import *

# Global variable to hold the DataFrame
_shared_event_log = None

def init_pool(df):
    global _shared_event_log
    _shared_event_log = df

def task_wrapper(args: tuple[str, str, str]) -> tuple[tuple[str, str], float]:
    kind, f1, f2 = args
    if kind == "disc-disc":
        val = MI_discrete_discrete(_shared_event_log, f1, f2)
    elif kind == "disc-cont":
        val = MI_discrete_continuous(_shared_event_log, f1, f2)
    elif kind == "cont-cont":
        val = MI_continuous_continuous(_shared_event_log, f1, f2)
    else:
        raise ValueError(f"Unknown task type: {kind}")
    return (f1, f2), val

def calculate_mi_matrix(
    event_log: pd.DataFrame,
    target_column: str,
    continuous_feature_columns: list[str],
    nominal_feature_columns: list[str],
) -> dict[tuple[str, str], float]:
    
    tasks = []

    # Categorical-categorical
    for i, f1 in enumerate(nominal_feature_columns):
        for f2 in nominal_feature_columns[i+1:]:
            tasks.append(("disc-disc", f1, f2))

    # Categorical-continuous
    for f1 in nominal_feature_columns:
        for f2 in continuous_feature_columns:
            tasks.append(("disc-cont", f1, f2))

    # Continuous-continuous
    for i, f1 in enumerate(continuous_feature_columns):
        for f2 in continuous_feature_columns[i+1:]:
            tasks.append(("cont-cont", f1, f2))

    # Target MI
    for f1 in nominal_feature_columns:
        tasks.append(("disc-cont", f1, target_column))
    for f1 in continuous_feature_columns:
        tasks.append(("cont-cont", f1, target_column))

    mi = {}

    with Pool(processes=cpu_count(), initializer=init_pool, initargs=(event_log,)) as pool:
        for (f1, f2), value in tqdm(pool.imap_unordered(task_wrapper, tasks), total=len(tasks), desc="Computing MI"):
            mi[(f1, f2)] = value
            mi[(f2, f1)] = value  # symmetric

    return mi

def calculate_maximal_relevance_minimal_redundancy_split(
    mi_matrix : dict[tuple[str, str], float],
    target_column : str,
    continuous_feature_columns : list[str],
    nominal_feature_columns : list[str]
) -> tuple[float, dict[str, float]]:
    # argmax_i( I(f_i, y) - 1/|S| sum_{j}(I(f_i, f_j))
    input_features = nominal_feature_columns + continuous_feature_columns
    mrmr = dict()
    for input_feature in input_features:
        mrmr[input_feature] = mi_matrix[(input_feature, target_column)] -\
                              sum([mi_matrix[(input_feature, other_feature)] for other_feature in input_features])/len(input_features)
    
    return max(mrmr, key=mrmr.get), mrmr
        

"""
    mi = dict()
    # for each feature calculate MI with target column and with other columns
    # begin with the categorical features
    for i, nominal_feature in enumerate(nominal_feature_columns):
        # consider only features with higher i because of the symmetric property of MI
        other_features = nominal_feature_columns[i+1:]
        for other_feature in other_features:
            cmi = MI_discrete_discrete(event_log, nominal_feature, other_feature)
            mi[(nominal_feature, other_feature)] = cmi
            mi[(other_feature, nominal_feature)] = cmi

        for other_feature in continuous_feature_columns:
            cmi = MI_discrete_continuous(event_log, nominal_feature, other_feature)
            mi[(nominal_feature, other_feature)] = cmi
            mi[(other_feature, nominal_feature)] = cmi

        mi[(nominal_feature, target_column)] = MI_discrete_continuous(event_log, nominal_feature, target_column)

    for i, continuous_feature in enumerate(continuous_feature_columns):
        other_features = continuous_feature_columns[i+1:]
        for other_feature in other_features:
            cmi = MI_continuous_continuous(event_log, continuous_feature, other_feature)
            mi[(continuous_feature, other_feature)] = cmi
            mi[(other_feature, continuous_feature)] = cmi
    
        mi[(continuous_feature, target_column)] = MI_continuous_continuous(event_log, continuous_feature, target_column)

    


    
    for i, nominal_feature in enumerate(continuous_feature_columns):
"""