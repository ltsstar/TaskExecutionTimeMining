#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location < - './bpic_clean.csv'

x_values_categorical <- c('org.resource', 'concept.name')
x_values_continous <- c('case.AMOUNT_REQ_start')
y_value <- 'duration_seconds'


nburn <- 10000
nsim <- 100
nthin <- 100


