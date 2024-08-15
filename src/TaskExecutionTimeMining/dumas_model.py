import numpy as np
import pandas
import itertools
from pix_framework.statistics.distribution import DurationDistribution, get_best_fitting_distribution, DistributionType

from event_log_transformer import TransformEventLog

class DumasModel:
    def __init__(self, event_log):
        self.min_n = 15
        self.event_log = event_log
        self.parse_event_log()
        self.set_up_models()

    def sample_action(self, action, concept, resource):
        if action == 'schedule':
            return self.sample_model(self.general_schedule_start_model, self.schedule_start_models,
                                     concept, resource)
        elif action == 'start':
            return self.sample_model(self.general_start_suspend_model, self.start_suspend_models,
                                     concept, resource)
        elif action == 'suspend':
            return self.sample_model(self.general_suspend_resume_model, self.suspend_resume_models,
                                     concept, resource)

    def sample_model(self, general_model, models, concept, resource):
        if (concept, resource) in models:
            return models[(concept, resource)].generate_sample(1)[0]
        else:
            return general_model.generate_sample(1)[0]

    def parse_event_log(self):
        self.schedule_start_event_log = TransformEventLog.start_end_event_log_mult(self.event_log.copy(),
                                                                    start_name_1='schedule',
                                                                    complete_name_1 = 'start',
                                                                    complete_name_2 = 'ate_abort',
                                                                    complete_name_3 = 'pi_abort',
                                                                   start_name_gen='_schedule',
                                                                   complete_name_gen='_start')

        self.start_suspend_event_log = TransformEventLog.start_end_event_log_mult(self.event_log.copy(),
                                                                            start_name_1='start',
                                                                            start_name_2='resume',
                                                                            complete_name_1 = 'suspend',
                                                                            complete_name_2 = 'ate_abort',
                                                                            complete_name_3 = 'complete',
                                                                        start_name_gen='_start',
                                                                        complete_name_gen='_suspend')

        self.suspend_resume_event_log = TransformEventLog.start_end_event_log_mult(self.event_log.copy(),
                                                                            start_name_1='suspend',
                                                                            complete_name_1 = 'resume',
                                                                            complete_name_2 = 'ate_abort',
                                                                            complete_name_3 = 'complete',
                                                                        start_name_gen='_suspend',
                                                                        complete_name_gen='_resume')

    def set_up_models(self):
        self.general_schedule_start_model = self.get_general_model(self.schedule_start_event_log)
        self.general_start_suspend_model = self.get_general_model(self.start_suspend_event_log)
        self.general_suspend_resume_model = self.get_general_model(self.suspend_resume_event_log)

        self.schedule_start_models = self.get_concept_resource_model(self.schedule_start_event_log,
                                                                     '_start')
        self.start_suspend_models = self.get_concept_resource_model(self.start_suspend_event_log,
                                                                    '_suspend')
        self.suspend_resume_models = self.get_concept_resource_model(self.suspend_resume_event_log,
                                                                     '_resume')

    def get_general_model(self, start_end_event_log):
        return get_best_fitting_distribution(start_end_event_log['duration_seconds'])

    def get_concept_resource_model(self, start_end_event_log, resource_suffix):
        models = dict()
        concepts = start_end_event_log['concept:name'].unique()
        resources = start_end_event_log['org:resource'+resource_suffix].unique()
        for concept, resource in itertools.product(concepts, resources):
            differentiated_durations = self.get_differentiated_durations(start_end_event_log, concept, resource, resource_suffix)
            if len(differentiated_durations) >= self.min_n:
                model = get_best_fitting_distribution(differentiated_durations)
                if model.type != DistributionType.FIXED:
                    models[(concept, resource)] = model
        return models

    def get_differentiated_durations(self, start_end_event_log, concept, resource, resource_suffix):
        el = start_end_event_log[(start_end_event_log['concept:name'] == concept) &
                                 (start_end_event_log['org:resource'+resource_suffix] == resource)]
        return el['duration_seconds']
