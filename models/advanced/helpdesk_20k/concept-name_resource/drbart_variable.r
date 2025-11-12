#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- 'data.csv'

x_values_categorical <- c('Resource_start','Activity_start'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			#'seconds_in_day'
)
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50


