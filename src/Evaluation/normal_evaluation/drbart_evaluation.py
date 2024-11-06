from normal_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_Normal(SampleOutcomes_Normal):
    def __init__(self, case_event_log, drbart_model, resources=True,
                max_sample=10, **kwargs):
        super().__init__(case_event_log, resources, **kwargs)
        self.drbart_model = drbart_model
        self.max_sample = max_sample


class SampleOutcomes_DRBART_Normal_A(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time =  lambda : self.drbart_model.sample([concept_name],
                                            [])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_R(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([resource],
                                            [])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(resource)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_R_S(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([resource],
                                            [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, resource)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_A_R(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                                 concept_name,
                                                 resource
        ],
                                            [])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, resource)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_A_R_S(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([concept_name, resource,
                                            ],
                                            [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, resource, seconds_in_day)
            return 0
        else:
            return sampled_time
        

class SampleOutcomes_DRBART_Normal_A_R_S_D(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([concept_name,
                                            resource,
                                            day_of_week
                                            ],
                                            [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, resource, seconds_in_day, day_of_week)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_A_R_S_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, case_event_log, drbart_model,
                 known_activities, **kwargs):
        super().__init__(case_event_log, drbart_model, **kwargs)
        self.known_activities = known_activities

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        resource,
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in self.known_activities],
                                        ],
                                        [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name,  resource, seconds_in_day, activity_count)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_A_R_S_RC(SampleOutcomes_DRBART_Normal):
    def __init__(self, case_event_log, drbart_model,
                 known_resources, **kwargs):
        super().__init__(case_event_log, drbart_model, **kwargs)
        self.known_resources = known_resources

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([concept_name,
                                        resource,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in self.known_resources]
                                        ],
                                        [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name,  resource, seconds_in_day, resource_count)
            return 0
        else:
            return sampled_time


class SampleOutcomes_DRBART_Normal_A_R_S_RC_AC(SampleOutcomes_DRBART_Normal):
    def __init__(self, case_event_log, drbart_model,
                 known_activities, known_resources, **kwargs):
        super().__init__(case_event_log, drbart_model, **kwargs)
        self.known_activities = known_activities
        self.known_resources = known_resources

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        resource,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in self.known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in self.known_activities],
                                        ],
                                        [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name,  resource, seconds_in_day, activity_count, resource_count)
            return 0
        else:
            return sampled_time
        