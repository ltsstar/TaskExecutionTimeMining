from typing import Tuple
import numpy as np
import pandas as pd
from collections import OrderedDict
import pickle
import hashlib
from typing import Tuple, Any, Literal
from sklearn.ensemble import HistGradientBoostingRegressor

CacheMode = Literal["cached", "uncached", "force_fresh"]

class QuantileRegression:
    def __init__(self,
                 event_log: pd.DataFrame,
                 attributes: dict,
                 target: str = 'duration_seconds',
                 cache_size: int = 500
                 ):
        # predict median=mean and first std. deviation
        self.event_log = event_log
        self.attributes = attributes
        self.target = target
        self.median_reg = HistGradientBoostingRegressor(
            loss='quantile',
            quantile=0.50,
            #max_iter=50,
            #min_samples_leaf=10,
            #max_depth=15
        )
        self.upper_reg = HistGradientBoostingRegressor(
            loss='quantile',
            quantile=0.8413,
            #max_iter=50,
            #min_samples_leaf=10,
            #max_depth=15
        )
        self._cache = OrderedDict()
        self.cache_size = cache_size

    def _encode_df(self):
        mappings = dict()
        encoded_columns = {}
        for col in self.attributes:
            codes, uniques = pd.factorize(self.event_log[col])
            mappings[col] = {cat: code for code, cat in enumerate(uniques)}
            encoded_columns[col] = codes
        encoded_data = pd.DataFrame(encoded_columns)
        x = encoded_data.astype(float).to_numpy()
        y = self.event_log[self.target]
        return x, y, mappings

    def fit(self):
        x, y, mappings = self._encode_df()
        self.mappings = mappings
        self.median_reg.fit(x, y)
        self.upper_reg.fit(x, y)
        del self.event_log  # free memory

    def _encode_with_mapping(self, df):
        encoded_columns = {}
        for col in self.attributes:
            mapping = self.mappings[col]
            if col not in df:
                encoded_columns[col] = 0
            else:
                encoded_columns[col] = df[col].map(mapping).fillna(-1).astype(int)
        encoded_data = pd.DataFrame(encoded_columns)
        x = encoded_data.astype(float).to_numpy()
        return x

    def _row_to_tuple(self, row: pd.Series) -> Tuple[Any, ...]:
        """Convert row to immutable tuple for hashing."""
        return tuple(row.get(col, None) for col in self.attributes)

    def _hash_row(self, row_tuple: Tuple) -> str:
        """Fast, stable hash."""
        return hashlib.md5(pickle.dumps(row_tuple)).hexdigest()

    def _encode_row_to_numpy(self, row: pd.Series) -> np.ndarray:
        encoded = []
        for col in self.attributes:
            mapping = self.mappings[col]
            val = row.get(col, None)
            code = mapping.get(val, -1)  # unknown → -1
            encoded.append(float(code))
        return np.array(encoded, dtype=float).reshape(1, -1)

    def _predict_single(self, x: np.ndarray) -> Tuple[float, float]:
        pred_median = self.median_reg.predict(x)
        pred_upper = self.upper_reg.predict(x)
        mu = float(pred_median)
        sigma = max(float(pred_upper - mu), 1e-8)  # prevent zero/negative sigma
        return mu, sigma

    def predict(self, df: pd.DataFrame, mode: CacheMode = "cached") -> np.ndarray:
        """
        mode:
          "cached" – use cache, fill on miss (default, fast)
          "uncached" – never read/write cache (slow, fresh)
          "force_fresh" – always recompute, ignore hits (for ablation)
        """
        if mode == "uncached":
            # completely bypass cache
            results = []
            for _, row in df.iterrows():
                x = self._encode_row_to_numpy(row)
                results.append(self._predict_single(x))
            return np.array(results)

        results = []
        for _, row in df.iterrows():
            row_tuple = self._row_to_tuple(row)
            row_hash = self._hash_row(row_tuple)
            # "force_fresh" → pretend miss even if hit
            if mode == "force_fresh" or row_hash not in self._cache:
                x = self._encode_row_to_numpy(row)
                mu_sigma = self._predict_single(x)
                # only write to cache in normal "cached" mode
                if mode == "cached":
                    self._cache[row_hash] = mu_sigma
                    if len(self._cache) > self.cache_size:
                        self._cache.popitem(last=False)  # evict LRU
            else:
                mu_sigma = self._cache[row_hash]
                if mode == "cached":
                    self._cache.move_to_end(row_hash)  # mark as recently used
            results.append(mu_sigma)
        return np.array(results)  # (n_rows, 2)

    def sample(self, df: pd.DataFrame, mode: CacheMode = "cached") -> np.ndarray:
        """Vectorized sampling with cache control."""
        mu_sigma = self.predict(df, mode=mode)
        samples = np.random.normal(
            mu_sigma[:, 0],
            np.maximum(mu_sigma[:, 1], 1e-8)
        )
        return samples