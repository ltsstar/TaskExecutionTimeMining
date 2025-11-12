#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/Helpdesk_train.csv'

x_values_categorical <- c('Resource_start', 'Activity_start',
			  'Assign.seriousness', 'Closed', 'Create.SW.anomaly', 'DUPLICATE', 'INVALID', 'Insert.ticket', 'RESOLVED', 'Require.upgrade', 'Resolve.SW.anomaly', 'Resolve.ticket', 'Schedule.intervention', 'Take.in.charge.ticket', 'VERIFIED', 'Wait'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


