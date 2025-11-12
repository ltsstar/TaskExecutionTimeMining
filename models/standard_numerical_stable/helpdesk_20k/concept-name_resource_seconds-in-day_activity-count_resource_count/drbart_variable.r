#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/Helpdesk_train.csv'

x_values_categorical <- c('Resource_start', 'Activity_start',
							'Assign.seriousness', 'Closed', 'Create.SW.anomaly', 'DUPLICATE', 'INVALID', 'Insert.ticket', 'RESOLVED', 'Require.upgrade', 'Resolve.SW.anomaly', 'Resolve.ticket', 'Schedule.intervention', 'Take.in.charge.ticket', 'VERIFIED', 'Wait',
							'Value.1', 'Value.10', 'Value.11', 'Value.12', 'Value.13', 'Value.14', 'Value.15', 'Value.16', 'Value.17', 'Value.18', 'Value.19', 'Value.2', 'Value.20', 'Value.21', 'Value.22', 'Value.3', 'Value.4', 'Value.5', 'Value.6', 'Value.7', 'Value.8', 'Value.9'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


