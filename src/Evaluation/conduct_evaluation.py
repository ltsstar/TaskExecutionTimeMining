from scipy.stats import gaussian_kde
from matplotlib import pyplot as plt
import matplotlib.dates as md
import datetime
import pandas
from tqdm import tqdm

class ConductEvaluation:
    def __init__(self,
                 trained_model,
                 sample_model_type,
                 sample_model_kwargs,
                 event_log,
                 n=1000):
        self.sample_model = sample_model_type(event_log, trained_model, **sample_model_kwargs)
        self.event_log = event_log
        self.n = n


    def _sample_case_from_model(self, case_log):
        pass

    def _get_kde_from_samples(self, samples, ground_truth):
        kde = gaussian_kde(samples).pdf(ground_truth)[0]
        return kde
    
    def _get_real_start_time(self, case_log):
        start_time = case_log['time:timestamp_start'].min().timestamp()
        return start_time
    
    def _get_real_end_time(self, case_log):
        end_time = case_log['time:timestamp_complete'].max().timestamp()
        return end_time
    
    def _plot_case(self, case_samples, real_start_time_ts, real_end_time_ts):
        real_end_time = datetime.datetime.fromtimestamp(real_end_time_ts)
        real_start_time = datetime.datetime.fromtimestamp(real_start_time_ts)
        case_samples_dt = [datetime.datetime.fromtimestamp(case_sample) for case_sample in case_samples]

        plt.figure(figsize=(14, 6))
        #plt.xticks( rotation=25 )
        #print(case_samples)
        ax=plt.gca()
        xfmt = md.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_major_locator(md.HourLocator(interval=4))
        mxfmt = md.DateFormatter('%H')
        ax.xaxis.set_minor_formatter(mxfmt)
        ax.xaxis.set_minor_locator(md.HourLocator(interval=1))
        ax.tick_params(axis='both', which='major', labelsize=8, rotation=90)
        ax.tick_params(axis='both', which='minor', labelsize=5, rotation=90)
        
        plt.gcf().autofmt_xdate()
        plt.gcf().set_dpi(300)
        plt.hist(case_samples_dt,
                 bins=pandas.date_range(start= pandas.to_datetime(min(case_samples_dt)).floor('D'),
                                        end=pandas.to_datetime(max(case_samples_dt)).ceil('D'),
                                        freq='30T'),
                 density=True)
        plt.axvline(x=real_end_time, color='red')
        plt.axvline(x=real_start_time, color='blue')
        plt.show()

    def sample_cases(self, plot_cases=False):
        cases = self.event_log['case:concept:name'].unique()
        results = dict()
        for case_name in tqdm(cases):
            case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
            real_start_time_ts = self._get_real_start_time(case_log)
            real_end_time_ts = self._get_real_end_time(case_log)

            case_samples = [self.sample_model.sample_case(case_name) for i in range(self.n)]
            likelihood = self._get_kde_from_samples(case_samples, real_end_time_ts)

            if plot_cases:
                self._plot_case(case_samples, real_start_time_ts, real_end_time_ts)
            results[case_name] = likelihood
        return results
