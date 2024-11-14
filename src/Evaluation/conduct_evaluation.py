from scipy.stats import gaussian_kde
from matplotlib import pyplot as plt
import matplotlib.dates as md
import datetime
import pandas
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
import io
import pickle
import copy
import numpy
from decimal import *

class ConductEvaluation:
    def __init__(self,
                 trained_model,
                 sample_model_type,
                 sample_model_kwargs,
                 event_log,
                 n=1000,
                 n_processes=10):
        self.sample_model = sample_model_type(event_log, trained_model, **sample_model_kwargs)
        self.event_log = event_log
        self.n = n
        self.n_processes = n_processes


    def _sample_case_from_model(self, case_log):
        pass

    @staticmethod
    def _get_kde_from_samples(samples, ground_truth):
        #kde = gaussian_kde(samples).pdf(ground_truth)[0]
        k = lambda x, h : (Decimal(1) / (Decimal(h) * Decimal(numpy.sqrt(2 * numpy.pi)))) * Decimal(numpy.e)**(Decimal(-0.5) * (Decimal(x) / Decimal(h))**Decimal(2))
        
        iqr = numpy.percentile(samples, 75) - numpy.percentile(samples, 25)
        h = 0.9 * min(numpy.std(samples), iqr/1.34) * len(samples)**(-1/5) # silverman rule
        #h = 1800**2
        #if iqr == 0 or h== 0:
        #    print(samples)
        #    print(ground_truth)
        kde = Decimal(1)/Decimal(len(samples)) * sum([k(ground_truth - sample, h) for sample in samples]) 
        return kde*24*3600

    @staticmethod
    def _get_kde_from_samples_args(args):
        return ConductEvaluation._get_kde_from_samples(args[0], args[1])
    
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

    def get_case_data(self, case_name):
        case_log = self.event_log[self.event_log['case:concept:name'] == case_name]
        real_start_time_ts = self._get_real_start_time(case_log)
        real_end_time_ts = self._get_real_end_time(case_log)
        return (case_name, case_log, real_start_time_ts, real_end_time_ts)

    def sample_case(self, case_log):
        case_samples = [self.sample_model.sample_case(case_log) for i in range(self.n)]
        return case_samples

    @staticmethod
    def sample_case_static(case_log, sample_model, n):
        return [sample_model.sample_case(case_log) for i in range(n)]

    def sample_cases(self, plot_cases=False, multiprocessing=True):
        cases = self.event_log['case:concept:name'].unique()
        results = dict()

        if multiprocessing:
            #prepare case data
            case_data = dict([(case_name, self.get_case_data(case_name)) for case_name in cases])

            with Pool(processes=self.n_processes) as pool:
                # Use `imap` to track progress with tqdm
                func = partial(ConductEvaluation.sample_case_static, sample_model=self.sample_model, n=self.n)
                sample_results = list(tqdm(pool.imap(func, [c[1] for c in case_data.values()]), total=len(cases)))

            with Pool(processes=self.n_processes) as pool:
                #func = lambda i, c : self.__get_kde_from_samples(sample_results[i], case_data[c][3])
                rr = list(tqdm(pool.imap(ConductEvaluation._get_kde_from_samples_args, [(sample_results[i], case_data[c][3]) for i, c in enumerate(case_data)]), total=len(case_data)))
                return_results = dict([(c, rr[i]) for i, c in enumerate(case_data)])
                #return_results = dict([(c, self._get_kde_from_samples(sample_results[i], case_data[c][3])) for i, c in enumerate(case_data)])
        else:
            case_data = dict()
            sample_results = []
            return_results = dict()
            func = partial(ConductEvaluation.sample_case_static, sample_model=self.sample_model, n=self.n)
            for c in tqdm(cases):
                case_data[c] = self.get_case_data(c)
                r = func(case_data[c][1])
                sample_results.append(r)
                kde = ConductEvaluation._get_kde_from_samples(r, case_data[c][3])
                kde2 = gaussian_kde(r).pdf(case_data[c][3])[0]
                if plot_cases:
                    print(c, kde, kde2, kde.ln(), numpy.log(kde2))
                    self._plot_case(r, case_data[c][2], case_data[c][3])
                return_results[c] = kde
            #return_results = dict([(c, ConductEvaluation._get_kde_from_samples(sample_results[i], case_data[c][3])) for i, c in enumerate(case_data)]) 

        return return_results, sample_results, case_data
