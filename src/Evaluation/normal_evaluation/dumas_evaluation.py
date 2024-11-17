from normal_evaluation.normal_evaluation import *

class SampleOutcomes_Dumas_Normal(SampleOutcomes_Normal):
    def __init__(self, case_event_log, dumas_model, resources=True,
                max_sample=10, **kwargs):
        super().__init__(case_event_log, resources, **kwargs)
        self.dm = dumas_model
        self.max_sample = max_sample

    def sample_duration(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week, value):
        sample_time = lambda : self.dm.sample(concept_name, resource)
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time, concept_name)
            return 0
        else:
            return sampled_time