#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name',
			  'day_of_week'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 750
nsim <- 50
nthin <- 5


