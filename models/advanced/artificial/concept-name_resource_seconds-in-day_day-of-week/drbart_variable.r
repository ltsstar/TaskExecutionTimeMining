#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- 'data.csv'

x_values_categorical <- c('org.resource', 'concept.name',
			  'day_of_week'
)
x_values_continous <- c('seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50