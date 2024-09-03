#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name'#,
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			#'seconds_in_day'
)
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


