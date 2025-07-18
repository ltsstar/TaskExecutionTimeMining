#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/BPIC_19_train.csv'

x_values_categorical <- c('org.resource_start','concept.name_start'#,
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			#'seconds_in_day'
)
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


