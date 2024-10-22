from evaluation import *

class SampleOutcomes_DRBART_BPIC2017(SampleOutcomes_BPIC2017):
    def __init__(self, case_event_log, drbart_start_suspend, drbart_suspend_resume):
        super().__init__(case_event_log)
        self.drbart_start_suspend = drbart_start_suspend
        self.drbart_suspend_resume = drbart_suspend_resume

class SampleOutcomes_DRBART_BPIC2017_R(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time =  self.drbart_start_suspend.sample([resource],
                                            [])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        day_of_week
                                        ],
                                        [])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        

class SampleOutcomes_DRBART_BPIC2017_A(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time =  self.drbart_start_suspend.sample([concept_name],
                                            [])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        day_of_week
                                        ],
                                        [])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time


class SampleOutcomes_DRBART_BPIC2017_R_A(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time =  self.drbart_start_suspend.sample([resource,
                                            concept_name
                                            ],
                                            [])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        day_of_week
                                        ],
                                        [])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time


class SampleOutcomes_DRBART_BPIC2017_R_A_S(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time =  self.drbart_start_suspend.sample([resource,
                                            concept_name
                                            ],
                                            [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
    

class SampleOutcomes_DRBART_BPIC2017_R_A_S_AC_RC(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']
        sampled_time = self.drbart_start_suspend.sample([resource,
                                        concept_name,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities]
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
    
    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities]
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
        

class SampleOutcomes_DRBART_BPIC2017_R_A_S_D(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time =  self.drbart_start_suspend.sample([resource,
                                            concept_name,
                                            day_of_week
                                            ],
                                            [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time

    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        day_of_week
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time


class SampleOutcomes_DRBART_BPIC2017_R_A_S_D_AC_RC(SampleOutcomes_DRBART_BPIC2017):
    def sample_start_suspend_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']
        sampled_time = self.drbart_start_suspend.sample([resource,
                                        concept_name,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities],
                                        day_of_week
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_start_suspend_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time
    
    def sample_suspend_resume_time(self, seconds_in_day, resource, concept_name,
                                   resource_count, activity_count,
                                   day_of_week):
        known_resources = ["User_10","User_100","User_101","User_102","User_103","User_104","User_105","User_106","User_107","User_108","User_109","User_11","User_110","User_111","User_112","User_113","User_114","User_115","User_116","User_117","User_118","User_119","User_12","User_120","User_121","User_122","User_123","User_124","User_125","User_126","User_127","User_129","User_13","User_130","User_131","User_132","User_133","User_134","User_135","User_136","User_137","User_138","User_14","User_140","User_141","User_142","User_143","User_144","User_15","User_16","User_17","User_18","User_19","User_2","User_20","User_21","User_22","User_23","User_24","User_25","User_26","User_27","User_28","User_29","User_3","User_30","User_31","User_32","User_33","User_34","User_35","User_36","User_37","User_38","User_39","User_4","User_40","User_41","User_42","User_43","User_44","User_45","User_46","User_47","User_48","User_49","User_5","User_50","User_51","User_52","User_53","User_54","User_55","User_56","User_57","User_58","User_59","User_6","User_60","User_61","User_62","User_63","User_64","User_65","User_66","User_67","User_68","User_69","User_7","User_70","User_71","User_72","User_73","User_74","User_75","User_76","User_77","User_78","User_79","User_8","User_80","User_81","User_82","User_83","User_84","User_85","User_86","User_87","User_88","User_89","User_9","User_90","User_91","User_92","User_93","User_94","User_95","User_96","User_97","User_98","User_99"]
        known_activities = ['W_Assess potential fraud','W_Call after offers','W_Call incomplete files','W_Complete application','W_Handle leads','W_Validate application']
        sampled_time = self.drbart_suspend_resume.sample([resource,
                                        concept_name,
                                        *[0 if resource not in resource_count else resource_count[resource] for resource in known_resources],
                                        *[0 if activity not in activity_count else activity_count[activity] for activity in known_activities],
                                        day_of_week
                                        ],
                                        [seconds_in_day])[1][0]
        if sampled_time < 0:
            return self.sample_suspend_resume_time(seconds_in_day, resource, concept_name, resource_count, activity_count, day_of_week)
        else:
            return sampled_time