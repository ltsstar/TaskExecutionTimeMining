from PCR_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_PCR(SampleOutcomes_PCR):
    def __init__(self, case_event_log, drbart_model, resources=True, max_sample=10):
        super().__init__(case_event_log, resources)
        self.drbart_model = drbart_model
        self.max_sample = max_sample

class SampleOutcomes_DRBART_PCR_A(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model, max_sample=10):
        super().__init__(case_event_log, drbart_model, resources=False, max_sample=max_sample)

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, activity_count, seconds_in_day)
            return 0
        else:
            return sampled_time

class SampleOutcomes_DRBART_PCR_A_S(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model, max_sample=10):
        super().__init__(case_event_log, drbart_model, resources=False, max_sample=max_sample)


    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, activity_count, seconds_in_day)
            return 0
        else:
            return sampled_time
        
class SampleOutcomes_DRBART_PCR_A_S_AC(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model, max_sample=10):
        super().__init__(case_event_log, drbart_model, resources=False, max_sample=max_sample)


    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        known_activities = ['Callback timeout', 'Export result', 'Export to EMS', 'Match patient data', 'Receive sample state', 'Send notification', 'Wait for plate validation', 'timeout']
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities],
                                        ],
                                        [seconds_in_day])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, activity_count, seconds_in_day)
            return 0
        else:
            return sampled_time
        
class SampleOutcomes_DRBART_PCR_A_S_D(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model, max_sample=10):
        super().__init__(case_event_log, drbart_model, resources=False, max_sample=max_sample)


    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sample_time = lambda : self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [seconds_in_day,
                                         day_of_week])[1][0]
        for i in range(self.max_sample):
            sampled_time = sample_time()
            if sampled_time > 0:
                break
        if sampled_time < 0:
            print('warning sample time below 0:', sampled_time)
            print(concept_name, activity_count, seconds_in_day)
            return 0
        else:
            return sampled_time