#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name',
			  'User_1', 'User_10', 'User_100', 'User_101', 'User_102', 'User_103', 'User_104', 'User_105', 'User_106', 'User_107', 'User_108', 'User_109', 'User_11', 'User_110', 'User_111', 'User_112', 'User_113', 'User_114', 'User_115', 'User_116', 'User_117', 'User_118', 'User_119', 'User_12', 'User_120', 'User_121', 'User_122', 'User_123', 'User_124', 'User_125', 'User_126', 'User_127', 'User_128', 'User_129', 'User_13', 'User_130', 'User_131', 'User_132', 'User_133', 'User_134', 'User_135', 'User_136', 'User_137', 'User_138', 'User_139', 'User_14', 'User_140', 'User_141', 'User_142', 'User_143', 'User_144', 'User_145', 'User_146', 'User_147', 'User_148', 'User_149', 'User_15', 'User_16', 'User_17', 'User_18', 'User_19', 'User_2', 'User_20', 'User_21', 'User_22', 'User_23', 'User_24', 'User_25', 'User_26', 'User_27', 'User_28', 'User_29', 'User_3', 'User_30', 'User_31', 'User_32', 'User_33', 'User_34', 'User_35', 'User_36', 'User_37', 'User_38', 'User_39', 'User_4', 'User_40', 'User_41', 'User_42', 'User_43', 'User_44', 'User_45', 'User_46', 'User_47', 'User_48', 'User_49', 'User_5', 'User_50', 'User_51', 'User_52', 'User_53', 'User_54', 'User_55', 'User_56', 'User_57', 'User_58', 'User_59', 'User_6', 'User_60', 'User_61', 'User_62', 'User_63', 'User_64', 'User_65', 'User_66', 'User_67', 'User_68', 'User_69', 'User_7', 'User_70', 'User_71', 'User_72', 'User_73', 'User_74', 'User_75', 'User_76', 'User_77', 'User_78', 'User_79', 'User_8', 'User_80', 'User_81', 'User_82', 'User_83', 'User_84', 'User_85', 'User_86', 'User_87', 'User_88', 'User_89', 'User_9', 'User_90', 'User_91', 'User_92', 'User_93', 'User_94', 'User_95', 'User_96', 'User_97', 'User_98', 'User_99',
			  'W_Assess.potential.fraud__ate_abort', 'W_Assess.potential.fraud__complete', 'W_Assess.potential.fraud__resume', 'W_Assess.potential.fraud__schedule', 'W_Assess.potential.fraud__start', 'W_Assess.potential.fraud__suspend', 'W_Assess.potential.fraud__withdraw', 'W_Call.after.offers__ate_abort', 'W_Call.after.offers__complete', 'W_Call.after.offers__resume', 'W_Call.after.offers__schedule', 'W_Call.after.offers__start', 'W_Call.after.offers__suspend', 'W_Call.after.offers__withdraw', 'W_Call.incomplete.files__ate_abort', 'W_Call.incomplete.files__complete', 'W_Call.incomplete.files__resume', 'W_Call.incomplete.files__schedule', 'W_Call.incomplete.files__start', 'W_Call.incomplete.files__suspend', 'W_Complete.application__ate_abort', 'W_Complete.application__complete', 'W_Complete.application__resume', 'W_Complete.application__schedule', 'W_Complete.application__start', 'W_Complete.application__suspend', 'W_Handle.leads__complete', 'W_Handle.leads__resume', 'W_Handle.leads__schedule', 'W_Handle.leads__start', 'W_Handle.leads__suspend', 'W_Handle.leads__withdraw', 'W_Shortened.completion.__resume', 'W_Shortened.completion.__schedule', 'W_Shortened.completion.__start', 'W_Shortened.completion.__suspend', 'W_Validate.application__ate_abort', 'W_Validate.application__complete', 'W_Validate.application__resume', 'W_Validate.application__schedule', 'W_Validate.application__start', 'W_Validate.application__suspend'
		 	  )
x_values_continous <- c('case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


