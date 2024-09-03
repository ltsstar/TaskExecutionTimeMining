#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2020_DD_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'Declaration.APPROVED.by.ADMINISTRATION', 'Declaration.APPROVED.by.BUDGET.OWNER', 'Declaration.APPROVED.by.PRE_APPROVER', 'Declaration.FINAL_APPROVED.by.SUPERVISOR', 'Declaration.FOR_APPROVAL.by.ADMINISTRATION', 'Declaration.FOR_APPROVAL.by.PRE_APPROVER', 'Declaration.FOR_APPROVAL.by.SUPERVISOR', 'Declaration.REJECTED.by.ADMINISTRATION', 'Declaration.REJECTED.by.BUDGET.OWNER', 'Declaration.REJECTED.by.EMPLOYEE', 'Declaration.REJECTED.by.MISSING', 'Declaration.REJECTED.by.PRE_APPROVER', 'Declaration.REJECTED.by.SUPERVISOR', 'Declaration.SAVED.by.EMPLOYEE', 'Declaration.SUBMITTED.by.EMPLOYEE', 'Payment.Handled', 'Request.Payment'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


