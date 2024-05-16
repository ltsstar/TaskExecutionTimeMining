from .GMM import *
from .Wasserstein import *

import pandas
from tqdm import tqdm

class SplittingCriterion:
    def __init__(self, x_name, data, min_class_size):
        self.x_name = x_name
        self.data = data
        self.min_class_size = min_class_size

    def _find_best_split(self, left, right, best_split, split_value):
        left_gmm = AutoGMM(left)
        right_gmm = AutoGMM(right)
        wd = GMMsWassersteinDistance(left_gmm, right_gmm).calculate()
        if best_split == None or wd > best_split[0]:
            return wd, split_value, left, right, left_gmm, right_gmm
        else:
            return best_split

    def _get_optimal_split_continous(self):
        unique_values = self.data[self.x_name].unique()
        best_split_value = None
        best_split = None
        for unique_value in tqdm(sorted(unique_values)):
            left = self.data[self.data[self.x_name] < unique_value]
            right = self.data[self.data[self.x_name] >= unique_value]
            if left.shape[0] < self.min_class_size or right.shape[0] < self.min_class_size:
                continue
            best_split = self._find_best_split(left, right, best_split, unique_value)
        return best_split

    def _get_optimal_split_categorical(self):
        unique_values = self.data[self.x_name].unique()
        best_split_value = None
        best_split = None
        for unique_value in tqdm(unique_values):
            left = self.data[self.data[self.x_name] == unique_value]
            right = self.data[self.data[self.x_name] != unique_value]
            if left.shape[0] < self.min_class_size or right.shape[0] < self.min_class_size:
                continue
            best_split = self._find_best_split(left, right, best_split, unique_value)
        return best_split
            
    def get_optimal_split(self):
        if pandas.api.types.is_integer_dtype(self.data[self.x_name]) \
                or pandas.api.types.is_float_dtype(self.data[self.x_name]):
            return self._get_optimal_split_continous()
        else:
            return self._get_optimal_split_categorical()

class DecisionTree:
    def __init__(self, min_class_size=50, min_wd_gain=100):
        self.min_class_size = min_class_size
        self.min_wd_gain = min_wd_gain

    def _rec_fit(self, event_log, gmm):
        best_split = None
        best_col = None
        for col in tqdm(event_log.columns):
            if col == 'duration_seconds':
                continue
            #print(col)
            split = SplittingCriterion(col, event_log, self.min_class_size).get_optimal_split()
            if split != None:
                if best_split[0] < split[0]:
                    best_split = split
                    best_col = col
        if best_split != None:
            print(best_col, best_split[0])
            left_result, right_result = None, None
            if GMMsWassersteinDistance(gmm, best_split[4]).calculate() > self.min_wd_gain:
                left_result = self._rec_fit(best_split[2], best_split[4])
            if GMMsWassersteinDistance(gmm, best_split[5]).calculate() > self.min_wd_gain:
                right_result = self._rec_fit(best_split[3], best_split[5])
            return [(best_col, best_split[1], best_split[0]), left_result, right_result]
        else:
            return None
                    
    
    def fit(self, start_end_event_log):
        gmm = AutoGMM(start_end_event_log)
        return self._rec_fit(start_end_event_log, gmm)

                
        