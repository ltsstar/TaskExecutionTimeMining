from normal_evaluation.normal_evaluation import *

class SampleOutcomes_Dumas_Normal(SampleOutcomes):
    def __init__(self, case_event_log, dumas_model):
        super().__init__(case_event_log)
        self.dm = dumas_model

    def sample_duration(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        return self.dm.sample_duration(concept_name, resource)