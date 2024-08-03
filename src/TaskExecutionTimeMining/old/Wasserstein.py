import numpy as np
from matplotlib import pyplot as plt
from sklearn.mixture import GaussianMixture
import scipy.stats as stats

class GMMsWassersteinDistance:
    def __init__(self, gmm1, gmm2):
        self.gmm_1, self.gmm_2 = gmm1, gmm2

    def calculate(self, n=1000, std_devs=3):
        return self._get_wasserstein_distance(n, std_devs)

    def _get_sample_range_2(self, gmm, std_devs):
        model_mean = np.sum([mean*weight for weight, mean in zip(gmm.gmm.weights_, gmm.gmm.means_)])
        model_variance = np.sum([weight * variance for weight, variance in zip(gmm.gmm.weights_, gmm.gmm.covariances_)])
        model_std_dev = np.sqrt(model_variance)
        return model_mean - std_devs * model_std_dev, model_mean + std_devs * model_std_dev

    def _get_sample_range(self, gmm, std_devs):
        return np.min(gmm.x), np.max(gmm.x)

    def _sample_ppf(self, gmm, sample_range, n):
        x = np.linspace(sample_range[0], sample_range[1], n)
        #x = np.arange(sample_range[0], sample_range[1], 0.5)
        y = np.exp(gmm.gmm.score_samples(np.ravel(x).astype(np.float64).reshape(-1,1)))
        #Below: required for ot only
        #y = np.exp(gmm.gmm.score_samples(np.ravel(x).astype(np.float64).reshape(-1,1))) * (sample_range[1] - sample_range[0]) / n
        # either len(x) or n
        return x, y


    def _get_wasserstein_distance(self, n, std_devs):
        #sample_ranges = [self._get_sample_range(self.gmm_1, std_devs),
        #                 self._get_sample_range(self.gmm_2, std_devs),
        #                 #self._get_sample_range_2(self.gmm_1, std_devs),
        #                 #self._get_sample_range_2(self.gmm_2, std_devs)
        #                ]
        #sample_range = min(zip(*sample_ranges))[0], max(zip(*sample_ranges))[1]
        #print(sample_range)
        #u_values, u_weights = self._sample_ppf(self.gmm_1, sample_range, n)
        #v_values, v_weights = self._sample_ppf(self.gmm_2, sample_range, n)
        #wd_1 = stats.wasserstein_distance(u_values, v_values, u_weights, v_weights)
        
        #sample only from ppfs
        gmm_1_samples, _ = self.gmm_1.gmm.sample(n)
        gmm_2_samples, _ = self.gmm_2.gmm.sample(n)
        wd_2 = stats.wasserstein_distance(gmm_1_samples.ravel(), gmm_2_samples.ravel())
        #return wd_1, wd_2
        return wd_2