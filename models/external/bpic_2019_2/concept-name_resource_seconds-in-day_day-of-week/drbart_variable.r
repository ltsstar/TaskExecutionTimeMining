#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '/dss/dsshome1/00/ge35xof4/TaskExecutionTimeMining/src/notebooks/transformed_event_logs/BPIC_2019_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'day_of_week'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_start',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 500
nsim <- 50
nthin <- 10


