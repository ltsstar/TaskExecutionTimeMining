#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/PCR_start_end_train.csv'

x_values_categorical <- c('concept.name',
			  'day_of_week',
			 'Callback.timeout', 'Export.result', 'Export.to.EMS', 'Match.patient.data', 'Receive.sample.state', 'Send.notification', 'Wait.for.plate.validation', 'timeout',
			  'intercase_n_1__Callback.timeout', 'intercase_n_1__Export.result', 'intercase_n_1__Export.to.EMS', 'intercase_n_1__Match.patient.data', 'intercase_n_1__Receive.sample.state', 'intercase_n_1__Send.notification', 'intercase_n_1__Wait.for.plate.validation', 'intercase_n_1__timeout'
)
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50


