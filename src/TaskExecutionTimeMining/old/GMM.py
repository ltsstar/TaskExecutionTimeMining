import numpy as np
from matplotlib import pyplot as plt
from sklearn.mixture import GaussianMixture
import scipy.stats as stats

class GMM:
    def __init__(self, start_end_event_log, n=10, percentile=False):
        self.durations = start_end_event_log['duration_seconds'].to_numpy()
        self._get_x(start_end_event_log, percentile)
        self.gmm = self.get_gmm(self.x, n)

    def _get_x(self, durations, percentile):
        if percentile:
            self.durations = self.durations[self.durations <= np.percentile(self.durations, percentile)]
        self.x = np.ravel(self.durations).astype(np.float64).reshape(-1,1)
    
    def get_gmm(self, x, n):
        mm = GaussianMixture(n,
                             covariance_type='full',
                             n_init=10,
                             #covariance_type='spherical',
                             init_params='k-means++',
                             #init_params='kmeans',
                             #init_params='random_from_data',
                             #init_params='random',
                             max_iter=1000
                            )
        mm.fit(x)
        return mm

    def get_pdf_values(self, f_axis):
        X = np.ravel(f_axis).astype(np.float64).reshape(-1,1)
        pdf = lambda x : sum([weight * stats.norm.pdf(x, mean, np.sqrt(cov))[0] \
                              for weight, mean, cov in zip(self.gmm.weights_, self.gmm.means_, self.gmm.covariances_)])
        return np.array([pdf(x) for x in X]).flatten()

    def goodness(self):
        #predictions = self.get_pdf_values(self.x)
        #gmm_samples, _ = self.gmm.sample(100000)
        #data_hist_weights, data_hist_bins = np.histogram(self.x, bins=min(200, int(len(self.x))), density=False)
        #sample_hist_weights, sample_hist_bins  = np.histogram(gmm_samples, bins=min(200, int(len(self.x))), density=False)

        #bins_2_values = lambda bins : [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
        #data_hist_values, sample_hist_values = bins_2_values(data_hist_bins), bins_2_values(sample_hist_bins)
        #wd_hist = stats.wasserstein_distance(data_hist_values, sample_hist_values, data_hist_weights, sample_hist_weights)
        #times_enlargen = int(100000 / len(self.x))
        #augmented_x = np.array([])
        #for i in range(times_enlargen):
        #    augmented_x = np.append(augmented_x, np.ravel(self.x))
        #wd_x = stats.wasserstein_distance(augmented_x, self.gmm.sample(len(augmented_x))[0].ravel())
        #wd_pdf = stats.wasserstein_distance(np.ravel(self.x), np.ravel(self.x), predictions, np.ones(self.x.shape))
        bic = self.gmm.bic(self.x)
        return bic
        #aic = self.gmm.aic(self.x)
        #return ot.wasserstein_1d(np.ravel(self.x), np.ravel(self.x), predictions)
        return wd_x#, wd_hist, wd_pdf, bic, aic
    
    def plot_gmm(self, other_gmm=None, show_all=True, percentile=False):
        # remove outliers
        if percentile:
            pruned_durations = self.durations[self.durations <= np.percentile(self.durations, percentile)]
        else:
            pruned_durations = self.durations
        f_axis = np.linspace(pruned_durations.min()-10, pruned_durations.max(), 10000)
        predictions = self.get_pdf_values(f_axis)
        plt.plot(f_axis, predictions)
        
        gmm_samples, _ = self.gmm.sample(100000)
        plt.hist(gmm_samples, bins=min(200, int(len(self.x))), histtype='bar', density=True, alpha=0.5, range=(pruned_durations.min(), pruned_durations.max()))
        #predictions = np.exp(self.gmm.score_samples(np.ravel(f_axis).astype(np.float64).reshape(-1,1)))
        #plt.plot(f_axis, predictions)
        if show_all:
            _, bins, patches = plt.hist(self.x, bins=min(200, int(len(self.x))), histtype='bar', density=True, alpha=0.5, range=(pruned_durations.min(), pruned_durations.max()))
            max_height = max([i.get_height() for i in patches])
            plt.ylim(0, max_height*1.1)
            for i in range(len(self.gmm.weights_)):
                plt.plot(f_axis,self.gmm.weights_[i]*stats.norm.pdf(f_axis,self.gmm.means_[i],np.sqrt(self.gmm.covariances_[i])).ravel(),
                        linestyle='dashed')

            plt.scatter(self.gmm.means_, [0]*len(self.gmm.means_), marker='o', color='red') 
            
            plt.rcParams['agg.path.chunksize'] = 10000
            plt.grid()

        if other_gmm:
            plt.plot(f_axis, other_gmm.get_pdf_values(f_axis))
        plt.show()

class AutoGMM(GMM):
    def __init__(self, start_end_event_log, percentile=False,
                max_gaussians=100, min_data_per_gaussian=15,
                min_relative_improvement=0.1,
                min_relative_improvement_period=3,
                max_fitting=5):
        self.n = 1
        super().__init__(start_end_event_log, self.n, percentile)
        goodness = self.goodness()
        max_gaussians = int(min(max_gaussians, len(self.x)/min_data_per_gaussian))
        non_improvement_period = 0
        for i in range(2, max_gaussians+1):
            self.get_gmm(self.x, i)
            super().__init__(start_end_event_log, i, percentile)
            new_goodness = self.goodness()
            self.n = i
            #print(self.n, goodness, (goodness - new_goodness) / goodness)
            if (goodness - new_goodness) / goodness < min_relative_improvement:
                non_improvement_period += 1
                if non_improvement_period >= min_relative_improvement_period:
                    break
            else:
                goodness = new_goodness
                non_improvement_period = 0
            if max_fitting > new_goodness:
                break        