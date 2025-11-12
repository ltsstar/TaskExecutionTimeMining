#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../../src/notebooks/transformed_event_logs/artificial_start_end_2_train.csv'

x_values_categorical <- c('concept.name', 'org.resource', 'day_of_week',
			  'X1', 'Clark', 'Jane', 'Joe', 'Karsten',
			  'DIAGNOSIS', 'QUALITY_CONTROL', 'REPAIR',
			  'intercase_n_1__DIAGNOSIS', 'intercase_n_1__QUALITY_CONTROL', 'intercase_n_1__REPAIR'
			  )
x_values_continous <- c('seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 7500
nsim <- 50
nthin <- 50


