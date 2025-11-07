import numpy as np
import pandas as pd
from sklearn_quantile import RandomForestQuantileRegressor

class QuantileRegression:
    def __init__(self,
                 event_log : pd.DataFrame, 
                 attributes : dict,
                 target : str = 'duration_seconds'
                 ):
        # predict median=mean and first std. deviation
        self.event_log = event_log
        self.attributes = attributes
        self.target = target
        self.qrf = RandomForestQuantileRegressor(q=[0.50, 0.8413])

    def _encode_df(self):
        encoded_data = pd.DataFrame()
        mappings = dict()
        for col in self.attributes:
            codes, uniques = pd.factorize(self.event_log[col])
            mappings[col] = {cat : code for code, cat in enumerate(uniques)}
            encoded_data[col] = codes
        x = encoded_data.astype(float).to_numpy()
        y = self.event_log[self.target]
        return x, y, mappings


    def fit(self):
        x, y, mappings = self._encode_df()
        self.mappings = mappings
        self.qrf.fit(x,y)

    def _encode_with_mapping(self, df):
        encoded_data = pd.DataFrame()
        for col in self.attributes:
            mapping = self.mappings[col]
            if col not in df:
                encoded_data[col] = 0
            else:
                encoded_data[col] = df[col].map(mapping).fillna(-1).astype(int)
        x = encoded_data.astype(float).to_numpy()
        return x

    def predict(self, df):
        x = self._encode_with_mapping(df)
        return self.qrf.predict(x)
    
    def predict_numpy(self, x):
        return self.qrf.predict(x)
    
    def _sample_from_prediction(self, prediction):
        mu = prediction[0]
        sigma = prediction[1] - prediction[0]
        sampled_duration = np.random.normal(mu, sigma)
        return sampled_duration

    def sample(self, df):
        pred = self.predict(df)
        sampled_durations = self._sample_from_prediction(pred)
        return sampled_durations
    
    def sample_numpy(self, x):
        pred = self.predict_numpy(x)
        sampled_durations = self._sample_from_prediction(pred)
        return sampled_durations