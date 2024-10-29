from PCR_evaluation.normal_evaluation import *

class SampleOutcomes_DRBART_PCR(SampleOutcomes_PCR):
    def __init__(self, case_event_log, drbart_model, resources=True):
        super().__init__(case_event_log, resources)
        self.drbart_model = drbart_model

class SampleOutcomes_DRBART_PCR_A(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model):
        super().__init__(case_event_log, drbart_model, resources=False)

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time = self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [])[1][0]
        if sampled_time < 0:
            return 0
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

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
            return 0
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        
class SampleOutcomes_DRBART_PCR_A_S_AC(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model):
        super().__init__(case_event_log, drbart_model, resources=False)

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        known_activities = ['case.concept.name', 'id.id_start', 'cpee.activity_start', 'cpee.instance_start', 'lifecycle.transition_start', 'cpee.lifecycle.transition_start', 'cpee.state_start', 'time.timestamp_start', 'data_start', 'cpee.description_start', 'concept.name', 'concept.endpoint_start', 'cpee.activity_uuid_start', 'raw_start', 'start_timestamp_start', 'id.id_complete', 'cpee.activity_complete', 'cpee.instance_complete', 'lifecycle.transition_complete', 'cpee.lifecycle.transition_complete', 'cpee.state_complete', 'time.timestamp_complete', 'data_complete', 'cpee.description_complete', 'concept.endpoint_complete', 'cpee.activity_uuid_complete', 'raw_complete', 'start_timestamp_complete', 'duration', 'duration_seconds', 'duration_ms', 'duration_hours', 'seconds_in_day', 'day_of_week', 'Callback.timeout', 'Export.result', 'Export.to.EMS', 'Match.patient.data', 'Receive.sample.state', 'Send.notification', 'Wait.for.plate.validation', 'timeout']
        sampled_time = self.drbart_model.sample([
                                        concept_name,
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities],
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return 0
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        
class SampleOutcomes_DRBART_PCR_A_S_D(SampleOutcomes_DRBART_PCR):
    def __init__(self, case_event_log, drbart_model):
        super().__init__(case_event_log, drbart_model, resources=False)

    def sample_duration(self, seconds_in_day, resource, concept_name,
                        resource_count, activity_count, day_of_week):
        sampled_time = self.drbart_model.sample([
                                        concept_name,
                                        ],
                                        [seconds_in_day,
                                         day_of_week])[1][0]
        if sampled_time < 0:
            return 0
            return self.sample_duration(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time