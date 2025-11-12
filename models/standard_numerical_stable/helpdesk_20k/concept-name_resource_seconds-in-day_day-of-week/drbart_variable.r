#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/Helpdesk_train.csv'

x_values_categorical <- c('Resource_start', 'Activity_start',
			  'day_of_week'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


