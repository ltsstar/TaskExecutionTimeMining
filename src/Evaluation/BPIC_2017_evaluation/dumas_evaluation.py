from evaluation import *

class SampleOutcomes_Dumas_BPIC2017(SampleOutcomes_BPIC2017):
    def __init__(self, case_event_log, dumas_model):
        super().__init__(case_event_log)
        self.dm = dumas_model

    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        return self.dm.sample_action('start', concept_name, resource)

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        return self.dm.sample_action('suspend', concept_name, resource)