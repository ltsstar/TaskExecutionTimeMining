#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- 'data.csv'

x_values_categorical <- c('org.resource_start')
x_values_continous <- c(#'case.RequestedAmount_suspend',
			#'seconds_in_day')
			)
y_value <- 'duration_seconds'


nburn <- 1000
nsim <- 25
nthin <- 25


