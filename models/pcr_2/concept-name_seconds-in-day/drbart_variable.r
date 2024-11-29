#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/PCR_start_end_train.csv'

x_values_categorical <- c(
			  'concept.name'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day'
		  	)
y_value <- 'duration_seconds'


nburn <- 100000
nsim <- 100
nthin <- 100


