#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2018_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'day_of_week'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


