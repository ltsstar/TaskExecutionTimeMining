#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/artificial_start_end_2.csv'

x_values_categorical <- c('org.resource')
x_values_continous <- c()
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


