import numpy as np
import collections
import pm4py
from pm4py.objects.petri_net import semantics


class SampleOutcomes:
    def __init__(self, case_event_log):
        self.event_log = case_event_log.copy()
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

    def sample_end_time(self):
        get_enabled_tasks = lambda marking : list(semantics.enabled_transitions(self.net, marking))

        marking = self.im
        current_time = self.start_time
        finish_time = dict() 
        activity_count = collections.defaultdict(lambda : collections.defaultdict(int))
        resource_count = collections.defaultdict(lambda : collections.defaultdict(int))
        while get_enabled_tasks(marking):
            pn_task = get_enabled_tasks(marking)[0]
            task, workitem, action = pn_task.label.split('__')
            row = self.event_log[self.event_log[self.new_concept_name] == pn_task.label].iloc[0]
            
            seconds_in_day = row['seconds_in_day']
            resource = row['org:resource']
            concept_name = row['concept:name']
            activity_count[action][row['concept:name']] += 1
            resource_count[action][row['org:resource']] += 1
        
            #print(action, concept_name, resource)
            
            if action == 'schedule':
                sampled_time = self.sample_schedule_start_time(seconds_in_day, resource, concept_name,
                                                               resource_count[action], activity_count[action])
                finish_time[task] = current_time + sampled_time
            elif action == 'start':
                sampled_time = self.sample_start_complete_time(seconds_in_day, resource, concept_name,
                                                               resource_count[action], activity_count[action])
                finish_time[task] += sampled_time
            elif action == 'suspend':
                sampled_time =  self.sample_suspend_resume_time(seconds_in_day, resource, concept_name,
                                                                resource_count[action], activity_count[action])
                finish_time[task] += sampled_time
            else:
                current_time = max(current_time, finish_time[task])
            if action in ['schedule', 'start', 'suspend']:
                pass
                #print(action, concept_name, sampled_time)
            marking = semantics.execute(pn_task, self.net, marking)

        #print('total:', current_time)
        #print('---------')
        return current_time


class SampleOutcomes_BPIC2017(SampleOutcomes):
    def __init__(self):
        super().__init__()

    def prepare_event_log(self):
        self.event_log['new_concept'] = self.event_log['concept:name'] +  '__' + self.event_log['EventID'] + '__' + self.event_log['lifecycle:transition']
        self.event_log = self.event_log[self.event_log['concept:name'].str.startswith('W_')]
        self.event_log = self.event_log.set_index('new_concept')
        self.new_concept_name = 'new_concept'

    def prepare_simulation(self):
        self.net, self.im, self.fm = pm4py.discover_petri_net_inductive(self.event_log,
                                                        activity_key='new_concept',
                                                        case_id_key='case:concept:name',
                                                        timestamp_key='time:timestamp')
        self.start_time = self.event_log['time:timestamp'].min().timestamp()


class SampleOutcomes_Dumas_BPIC2017(SampleOutcomes_BPIC2017):
    def __init__(self, dumas_model):


class SampleOutcomes_DRBART_BPIC2017(SampleOutcomes_BPIC2017):
    def __init__(self, drbart_schedule_start, drbart_start_suspend, drbart_suspend_resume):
        super().__init__()
        self.drbart_schedule_start = drbart_schedule_start
        self.drbart_start_suspend = drbart_start_suspend
        self.drbart_suspend_resume = drbart_suspend_resume


    def sample_schedule_start_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        known_resources = ['User_10','User_100','User_101','User_102','User_103','User_104','User_105','User_106','User_107','User_108','User_109','User_11','User_110','User_111','User_112','User_113','User_114','User_115','User_116','User_117','User_118','User_119','User_12','User_120','User_121','User_122','User_123','User_124','User_125','User_126','User_127','User_129','User_13','User_130','User_131','User_132','User_133','User_134','User_135','User_136','User_137','User_138','User_14','User_140','User_141','User_142','User_143','User_144','User_15','User_16','User_17','User_18','User_19','User_2','User_20','User_21','User_22','User_23','User_24','User_25','User_26','User_27','User_28','User_29','User_3','User_30','User_31','User_32','User_33','User_34','User_35','User_36','User_37','User_38','User_39','User_4','User_40','User_41','User_42','User_43','User_44','User_45','User_46','User_47','User_48','User_49','User_5','User_50','User_51','User_52','User_53','User_54','User_55','User_56','User_57','User_58','User_59','User_6','User_60','User_61','User_62','User_63','User_64','User_65','User_66','User_67','User_68','User_69','User_7','User_70','User_71','User_72','User_73','User_74','User_75','User_76','User_77','User_78','User_79','User_8','User_80','User_81','User_82','User_83','User_84','User_85','User_86','User_87','User_88','User_89','User_9','User_90','User_91','User_92','User_93','User_94','User_95','User_96','User_97','User_98','User_99']
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']

        duration_ms_log = self.drbart_schedule_start.sample([resource,
                                            concept_name,
                                            *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                            *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities]
                                            ],
                                            [seconds_in_day])[1][0]
        return np.exp(duration_ms_log - np.log(1000))

    def sample_start_complete_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']

        sampled_time =  self.drbart_start_suspend.sample([resource,
                                            concept_name,
                                            *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                            *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities]
                                            ],
                                            [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_start_complete_time(seconds_in_day, resource, concept_name, resource_count, activity_count)
        else:
            return sampled_time
    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities]
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count)
        else:
            return sampled_time



get_real_end_time = lambda case_name : event_log[event_log['case:concept:name'] == case_name]['time:timestamp'].max().timestamp()


