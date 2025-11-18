import pandas as pd
from normal_evaluation.normal_evaluation import *

class SampleOutcomes_QuantileRegression(SampleOutcomes_Normal):
    def __init__(self, quantile_regression_model,
                max_sample=10, **kwargs):
        super().__init__(**kwargs)
        self.qrm = quantile_regression_model
        self.max_sample = max_sample
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        raise NotImplementedError("This method should be implemented to sample from the quantile regression model.")

    def sample_duration(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week, value, inter_instance_counts):
        for i in range(self.max_sample):
            sampled_time = self.sample_from_model(seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week, value, inter_instance_counts)
            if sampled_time > 0:
                break
        if sampled_time < 0:
            #print('warning sample time below 0:', sampled_time, concept_name)
            return 0
        else:
            return sampled_time
        
class SampleOutcomes_QuantileRegression_A(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name]], columns=[self.activity_key])
        return self.qrm.sample(df)[0]
    
class SampleOutcomes_QuantileRegression_R(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[resource]], columns=[self.resource_key])
        return self.qrm.sample(df)[0]
    
class SampleOutcomes_QuantileRegression_AR(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource]], columns=[self.activity_key, self.resource_key])
        return self.qrm.sample(df)[0]
    
class SampleOutcomes_QuantileRegression_ARS(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day]], columns=[self.activity_key, self.resource_key, 'seconds_in_day'])
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ASAC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, seconds_in_day] + list(activity_count.values())],
                          columns=[self.activity_key, 'seconds_in_day'] + list(activity_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_RSRC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[resource, seconds_in_day] + list(resource_count.values())],
                          columns=[self.resource_key, 'seconds_in_day'] + list(resource_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ARSAC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day] + list(activity_count.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day'] + list(activity_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]


class SampleOutcomes_QuantileRegression_ARSRC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day] + list(resource_count.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day'] + list(resource_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]

    
class SampleOutcomes_QuantileRegression_ARSACRC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day] + list(activity_count.values()) + list(resource_count.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day'] + list(activity_count.keys()) + list(resource_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ARSD(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day, day_of_week]],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day', 'day_of_week'])
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ARSDACRC(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day, day_of_week] + list(activity_count.values()) + list(resource_count.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day', 'day_of_week'] + list(activity_count.keys()) + list(resource_count.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ARSDACRCII(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day, day_of_week] + list(activity_count.values()) + list(resource_count.values()) + list(inter_instance_columns.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day', 'day_of_week'] + list(activity_count.keys()) + list(resource_count.keys()) + list(inter_instance_columns.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
    
class SampleOutcomes_QuantileRegression_ARSDII(SampleOutcomes_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day, day_of_week] + list(inter_instance_columns.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day', 'day_of_week'] + list(inter_instance_columns.keys()))
        return self.qrm.sample(df, mode='uncached')[0]
