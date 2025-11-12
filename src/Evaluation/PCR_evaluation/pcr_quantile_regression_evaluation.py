from normal_evaluation.quantile_regression_evaluation import *
from PCR_evaluation.normal_evaluation import *


class SampleOutcomes_PCR_QuantileRegression(SampleOutcomes_QuantileRegression, SampleOutcomes_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, resources=False, **kwargs)


class SampleOutcomes_PCR_QuantileRegression_A(SampleOutcomes_PCR_QuantileRegression, SampleOutcomes_QuantileRegression_A):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SampleOutcomes_PCR_QuantileRegression_AS(SampleOutcomes_PCR_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, seconds_in_day]],
                          columns=[self.activity_key, 'seconds_in_day'])
        return self.qrm.sample(df)[0]


class SampleOutcomes_PCR_QuantileRegression_ASAC(SampleOutcomes_PCR_QuantileRegression, SampleOutcomes_QuantileRegression_ASAC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SampleOutcomes_PCR_QuantileRegression_ASD(SampleOutcomes_PCR_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, seconds_in_day, day_of_week]],
                          columns=[self.activity_key, 'seconds_in_day', 'day_of_week'])
        return self.qrm.sample(df)[0]


class SampleOutcomes_PCR_QuantileRegression_ASDII(SampleOutcomes_PCR_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, seconds_in_day, day_of_week] + list(inter_instance_columns.values())],
                          columns=[self.activity_key, 'seconds_in_day', 'day_of_week'] + list(inter_instance_columns.keys()))
        return self.qrm.sample(df)[0]


class SampleOutcomes_PCR_QuantileRegression_AASDACII(SampleOutcomes_PCR_QuantileRegression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sample_from_model(self, seconds_in_day, resource, concept_name,
                            resource_count, activity_count,
                            day_of_week, value, inter_instance_columns):
        df = pd.DataFrame([[concept_name, resource, seconds_in_day, day_of_week] + list(activity_count.values()) + list(inter_instance_columns.values())],
                          columns=[self.activity_key, self.resource_key, 'seconds_in_day', 'day_of_week'] + list(activity_count.keys()) + list(inter_instance_columns.keys()))
        return self.qrm.sample(df)[0]