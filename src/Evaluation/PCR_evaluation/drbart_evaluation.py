from functools import partial
from PCR_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_PCR(SampleOutcomes_PCR):
    def __init__(self, drbart_model, resources=True,
                 max_sample=10,
                 max_sample_value=3600*24*365,
                 **kwargs):
        super().__init__(resources, **kwargs)
        self.drbart_model = drbart_model
        self.max_sample = max_sample
        self.max_sample_value = max_sample_value
        self.categorical_args = []
        self.continuous_args = []

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week,
                        value, inter_instance_counts):

        continuous_variables = list()
        for cv in self.continuous_args:
            continuous_variables.append(eval(cv))
        categorical_variables = list()
        for cv in self.categorical_args:
            r = eval(cv)
            if type(r) is list:
                categorical_variables += r
            else:
                categorical_variables.append(r)
        pf = partial(self.drbart_model.sample,
                                    categorical_variables,
                                    continuous_variables
                    )
        sample_time = lambda : pf()[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0 and sampled_time < self.max_sample_value:
                break
        if sampled_time < 0:
            #print('warning sample time below 0:', sampled_time)
            #print(concept_name)
            return 0
        elif sampled_time > self.max_sample_value:
            #print('warning sample time above max:', sampled_time)
            #print(concept_name)
            return self.max_sample_value
        else:
            #print(categorical_variables, continuous_variables, sampled_time)
            return sampled_time


class SampleOutcomes_DRBART_PCR_A(SampleOutcomes_DRBART_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name']


class SampleOutcomes_DRBART_PCR_A_S(SampleOutcomes_DRBART_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name']
        self.continuous_args = ['seconds_in_day']

        
class SampleOutcomes_DRBART_PCR_A_S_AC(SampleOutcomes_DRBART_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)']
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']

        
class SampleOutcomes_DRBART_PCR_A_S_D(SampleOutcomes_DRBART_PCR):
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'day_of_week']
        self.continuous_args = ['seconds_in_day']

"""
Inter-instance
"""
class SampleOutcomes_DRBART_PCR_A_S_D_II(SampleOutcomes_DRBART_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name',
                                  'day_of_week',
                                  '(lambda inter_instance_count, inter_instance_columns : [0 if inter_instance_column not in inter_instance_count else inter_instance_count[inter_instance_column] for inter_instance_column in inter_instance_columns])(inter_instance_columns, self.inter_instance_columns)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.inter_instance_columns = kwargs['inter_instance_column_names']


"""
Inter-instance
"""
class SampleOutcomes_DRBART_PCR_A_S_D_AC_II(SampleOutcomes_DRBART_PCR):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name',
                                  'day_of_week',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)',
                                  '(lambda inter_instance_counts, inter_instance_column_names : [0 if inter_instance_column_name not in inter_instance_counts else inter_instance_counts[inter_instance_column_name] for inter_instance_column_name in inter_instance_column_names])(inter_instance_counts, self.inter_instance_column_names)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']
        self.inter_instance_columns = kwargs['inter_instance_column_names']