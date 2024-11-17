from functools import partial
from normal_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_Normal(SampleOutcomes_Normal):
    def __init__(self, case_event_log, drbart_model, resources=True,
                max_sample=10, **kwargs):
        super().__init__(case_event_log, resources, **kwargs)
        self.drbart_model = drbart_model
        self.max_sample = max_sample
        self.categorical_args = []
        self.continuous_args = []

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week,
                        value):

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
            if sampled_time > 0:
                break
        if sampled_time < 0:
            #print('warning sample time below 0:', sampled_time)
            #print(concept_name)
            return 0
        else:
            #print(categorical_variables, continuous_variables, sampled_time)
            return sampled_time

"""
concept-name
"""
class SampleOutcomes_DRBART_Normal_A(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name']


"""
resource
"""
class SampleOutcomes_DRBART_Normal_R(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource']


"""
concept-name_resource
"""
class SampleOutcomes_DRBART_Normal_A_R(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource']


class SampleOutcomes_DRBART_Normal_R_A(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name']


"""
concept-name_resource_seconds-in-day
"""
class SampleOutcomes_DRBART_Normal_A_R_S(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource']
        self.continuous_args = ['seconds_in_day']


class SampleOutcomes_DRBART_Normal_R_A_S(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name']
        self.continuous_args = ['seconds_in_day']


"""
concept-name_resource_seconds-in-day_activity-count
"""
class SampleOutcomes_DRBART_Normal_A_R_S_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)']
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']


class SampleOutcomes_DRBART_Normal_R_A_S_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)']
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']


"""
concept-name_resource_seconds-in-day_activity-count_resource_count
"""
class SampleOutcomes_DRBART_Normal_A_R_S_RC_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


class SampleOutcomes_DRBART_Normal_R_A_S_RC_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


"""
concept-name_resource_seconds-in-day_activity-count_resource_count_amount
"""
class SampleOutcomes_DRBART_Normal_A_R_S_RC_AC_V(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day', 'value']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


class SampleOutcomes_DRBART_Normal_R_A_S_RC_AC_V(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day', 'value']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


"""
concept-name_resource_seconds-in-day_day-of-week
"""
class SampleOutcomes_DRBART_Normal_A_R_S_D(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource', 'day_of_week']
        self.continuous_args = ['seconds_in_day']


class SampleOutcomes_DRBART_Normal_R_A_S_D(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name', 'day_of_week']
        self.continuous_args = ['seconds_in_day']


"""
concept-name_resource_seconds-in-day_day-of-week_activity-count_resoure-count
"""
class SampleOutcomes_DRBART_Normal_A_R_S_D_RC_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource',
                                  'day_of_week',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


class SampleOutcomes_DRBART_Normal_R_A_S_D_RC_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name',
                                  'day_of_week',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)',
                                  '(lambda activity_count, known_activities : [0 if activity not in activity_count else activity_count[activity] for activity in known_activities])(activity_count, self.known_activities)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_activities = kwargs['known_activities']
        self.known_resources = kwargs['known_resources']


"""
concept-name_resource_seconds-in-day_resource-count
"""
class SampleOutcomes_DRBART_Normal_A_R_S_RC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['concept_name', 'resource',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_resources = kwargs['known_resources']


class SampleOutcomes_DRBART_Normal_R_A_S_RC(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource', 'concept_name',
                                  '(lambda resource_count, known_resources : [0 if resource not in resource_count else resource_count[resource] for resource in known_resources])(resource_count, self.known_resources)'
                                 ]
        self.continuous_args = ['seconds_in_day']
        self.known_resources = kwargs['known_resources']


"""
Artificial: resource_seconds-in-day
"""
class SampleOutcomes_DRBART_Normal_R_S(SampleOutcomes_DRBART_Normal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorical_args =  ['resource']
        self.continuous_args = ['seconds_in_day']