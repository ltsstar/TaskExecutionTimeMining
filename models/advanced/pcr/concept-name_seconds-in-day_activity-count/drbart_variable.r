#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- 'data.csv'

x_values_categorical <- c('concept.name',
			 'Callback.timeout', 'Export.result', 'Export.to.EMS', 'Match.patient.data', 'Receive.sample.state', 'Send.notification', 'Wait.for.plate.validation', 'timeout'
)
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50


