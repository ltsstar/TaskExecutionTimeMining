from PCR_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_PCR(SampleOutcomes_PCR):
    def __init__(self, case_event_log, drbart_model, resources=True):
        super().__init__(case_event_log, resources)
        self.drbart_model = drbart_model


class SampleOutcomes_DRBART_PCR_A_S(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model):
        super().__init__(case_event_log, drbart_model, resources=False)

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time = self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            print('less than zero')
            return sampled_time
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time