#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name',
			  'W_Assess.potential.fraud__ate_abort', 'W_Assess.potential.fraud__complete', 'W_Assess.potential.fraud__resume', 'W_Assess.potential.fraud__schedule', 'W_Assess.potential.fraud__start', 'W_Assess.potential.fraud__suspend', 'W_Assess.potential.fraud__withdraw', 'W_Call.after.offers__ate_abort', 'W_Call.after.offers__complete', 'W_Call.after.offers__resume', 'W_Call.after.offers__schedule', 'W_Call.after.offers__start', 'W_Call.after.offers__suspend', 'W_Call.after.offers__withdraw', 'W_Call.incomplete.files__ate_abort', 'W_Call.incomplete.files__complete', 'W_Call.incomplete.files__resume', 'W_Call.incomplete.files__schedule', 'W_Call.incomplete.files__start', 'W_Call.incomplete.files__suspend', 'W_Complete.application__ate_abort', 'W_Complete.application__complete', 'W_Complete.application__resume', 'W_Complete.application__schedule', 'W_Complete.application__start', 'W_Complete.application__suspend', 'W_Handle.leads__complete', 'W_Handle.leads__resume', 'W_Handle.leads__schedule', 'W_Handle.leads__start', 'W_Handle.leads__suspend', 'W_Handle.leads__withdraw', 'W_Shortened.completion.__resume', 'W_Shortened.completion.__schedule', 'W_Shortened.completion.__start', 'W_Shortened.completion.__suspend', 'W_Validate.application__ate_abort', 'W_Validate.application__complete', 'W_Validate.application__resume', 'W_Validate.application__schedule', 'W_Validate.application__start', 'W_Validate.application__suspend'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


