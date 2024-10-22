class SampleOutcomes:
    def __init__(self, event_log):
        self.event_log = event_log.copy()
        self.prepare_event_log()
        self.prepare_simulation()

    def sample_schedule_start_time(seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        pass

    def sample_start_complete_time(seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        pass

    def sample_suspend_resume_time(seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        pass

    def prepare_event_log(self):
        pass

    def prepare_simulation(self):
        pass

    def sample_end_times(self, n=1000):
        return [self.sample_end_time() for i in range(n)]

    def sample_end_time(self, start_time, net, im):
        pass