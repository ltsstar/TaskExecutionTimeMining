#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- 'data.csv'

x_values_categorical <- c('org.resource', 'concept.name',
			  'day_of_week',
			  'DIAGNOSIS', 'QUALITY_CONTROL', 'REPAIR',
			  'X1', 'Clark', 'Jane', 'Joe', 'Karsten',
			  'intercase_n_1__DIAGNOSIS', 'intercase_n_1__QUALITY_CONTROL', 'intercase_n_1__REPAIR'
)
x_values_continous <- c('seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50