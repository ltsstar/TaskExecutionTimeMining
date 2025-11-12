#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/BPIC_19_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'day_of_week'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50


