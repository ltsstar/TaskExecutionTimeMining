from PCR_evaluation.normal_evaluation import *

class SampleOutcomes_Dumas_Normal(SampleOutcomes_PCR):
    def __init__(self, case_event_log, dumas_model, max_sample=10):
        super().__init__(case_event_log)
        self.dm = dumas_model
        self.max_sample = max_sample

    def sample_duration(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sample_time = lambda : self.dm.sample_action('start', concept_name, resource)
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time, concept_name)
            return 0
        else:
            return sampled_time