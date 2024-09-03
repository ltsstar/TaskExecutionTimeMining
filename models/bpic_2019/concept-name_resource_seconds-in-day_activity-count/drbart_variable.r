#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2019_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'Block.Purchase.Order.Item', 'Cancel.Goods.Receipt', 'Cancel.Invoice.Receipt', 'Cancel.Subsequent.Invoice', 'Change.Approval.for.Purchase.Order', 'Change.Currency', 'Change.Delivery.Indicator', 'Change.Final.Invoice.Indicator', 'Change.Price', 'Change.Quantity', 'Change.Rejection.Indicator', 'Change.Storage.Location', 'Change.payment.term', 'Clear.Invoice', 'Create.Purchase.Order.Item', 'Create.Purchase.Requisition.Item', 'Delete.Purchase.Order.Item', 'Reactivate.Purchase.Order.Item', 'Receive.Order.Confirmation', 'Record.Goods.Receipt', 'Record.Invoice.Receipt', 'Record.Service.Entry.Sheet', 'Record.Subsequent.Invoice', 'Release.Purchase.Order', 'Release.Purchase.Requisition', 'Remove.Payment.Block', 'SRM..Awaiting.Approval', 'SRM..Change.was.Transmitted', 'SRM..Complete', 'SRM..Created', 'SRM..Deleted', 'SRM..Document.Completed', 'SRM..Held', 'SRM..In.Transfer.to.Execution.Syst.', 'SRM..Incomplete', 'SRM..Ordered', 'SRM..Transaction.Completed', 'SRM..Transfer.Failed..E.Sys..', 'Set.Payment.Block', 'Update.Order.Confirmation', 'Vendor.creates.debit.memo', 'Vendor.creates.invoice'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150


