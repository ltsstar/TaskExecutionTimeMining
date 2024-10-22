from normal_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_Normal(SampleOutcomes_Normal):
    def __init__(self, case_event_log, drbart_model):
        super().__init__(case_event_log)
        self.drbart_model = drbart_model


class SampleOutcomes_DRBART_BPIC2017_R(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time =  self.drbart_model.sample([resource],
                                            [])[1][0]
        
        if sampled_time < 0:
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        



class SampleOutcomes_DRBART_Normal_R_A_S_D(SampleOutcomes_DRBART_Normal):
    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time =  self.drbart_model.sample([resource,
                                            concept_name,
                                            day_of_week
                                            ],
                                            [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        

class SampleOutcomes_DRBART_Normal_R_A_S_D_AC_RC(SampleOutcomes_DRBART_Normal):
    def __init__(self, case_event_log, drbart_model,
                 known_activities, known_resources):
        super().__init__(case_event_log, drbart_model)
        self.known_activities = known_activities
        self.known_resources = known_resources

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time = self.drbart_model.sample([resource,
                                        concept_name,
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in self.known_activities],
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in self.known_resources],
                                        day_of_week
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time