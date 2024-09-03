#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2018_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'abort.external', 'abort.payment', 'approve', 'begin.admissibility.check', 'begin.editing', 'begin.editing.from.refused', 'begin.payment', 'begin.preparations', 'calculate', 'calculate.protocol', 'cancel.offline', 'change.department', 'check', 'check.admissibility', 'clear', 'correction.GFM17', 'create', 'decide', 'discard', 'finish.editing', 'finish.payment', 'finish.pre.check', 'finish.preparations', 'initialize', 'insert.document', 'mail.income', 'mail.valid', 'performed', 'performed.offline', 'plan', 'prepare.external', 'prepare.offline', 'refuse', 'remove.document', 'restart.editing', 'revoke.approval', 'revoke.decision', 'revoke.withdrawal', 'save', 'take.original.document', 'withdraw'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


