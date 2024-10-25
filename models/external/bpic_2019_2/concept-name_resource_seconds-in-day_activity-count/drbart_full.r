#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '/dss/dsshome1/00/ge35xof4/TaskExecutionTimeMining/src/notebooks/transformed_event_logs/BPIC_2019_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'Block.Purchase.Order.Item', 'Cancel.Goods.Receipt', 'Cancel.Invoice.Receipt', 'Cancel.Subsequent.Invoice', 'Change.Approval.for.Purchase.Order', 'Change.Currency', 'Change.Delivery.Indicator', 'Change.Final.Invoice.Indicator', 'Change.Price', 'Change.Quantity', 'Change.Rejection.Indicator', 'Change.Storage.Location', 'Change.payment.term', 'Clear.Invoice', 'Create.Purchase.Order.Item', 'Create.Purchase.Requisition.Item', 'Delete.Purchase.Order.Item', 'Reactivate.Purchase.Order.Item', 'Receive.Order.Confirmation', 'Record.Goods.Receipt', 'Record.Invoice.Receipt', 'Record.Service.Entry.Sheet', 'Record.Subsequent.Invoice', 'Release.Purchase.Order', 'Release.Purchase.Requisition', 'Remove.Payment.Block', 'SRM..Awaiting.Approval', 'SRM..Change.was.Transmitted', 'SRM..Complete', 'SRM..Created', 'SRM..Deleted', 'SRM..Document.Completed', 'SRM..Held', 'SRM..In.Transfer.to.Execution.Syst.', 'SRM..Incomplete', 'SRM..Ordered', 'SRM..Transaction.Completed', 'SRM..Transfer.Failed..E.Sys..', 'Set.Payment.Block', 'Update.Order.Confirmation', 'Vendor.creates.debit.memo', 'Vendor.creates.invoice'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 500
nsim <- 50
nthin <- 10



#
# STATIC PART
#

library(purrr)
library(cleandata)
library(devtools)
library(jsonlite)
devtools::install_github('ltsstar/drbart', ref = 'main', force=FALSE)
library(drbart)


df <- read.csv(file_location)

col_names <- c(x_values_categorical, x_values_continous, y_value)
df_xy = na.omit(
  df[,col_names]
)

#free memory
rm(df)
gc()

enc <- lapply(x_values_categorical, function(x_value) {unique(df_xy[,x_value])})


df_xy <- lapply(names(df_xy), function(col_name) {
  x <- df_xy[[col_name]]
  names(col_name)[-1] <- col_name
  print(col_name)
  if(!is.null(col_name)
     && col_name %in% x_values_categorical) {
    return(as.numeric(factor(x, levels = unique(x))))
  } else {
    return(x)
  }
})
names(df_xy) <- col_names


enc2 <- lapply(enc, function(v) {as.numeric(labels(v))})
enc3 <- lapply(x_values_continous, function(name){
  return(
    seq(min(df_xy[[name]]), max(df_xy[[name]]),
        length.out = min(
          10000,
          length(df_xy[[name]])
        ))
  )
})

df_x = df_xy[names(df_xy) != y_value]


y <- df_xy[[y_value]]
#ul <- unlist(df_x)
ul <- purrr::flatten_dbl(df_x)

#free memory
rm(df_xy)
gc()

x <- matrix(
      ul,
      ncol = length(col_names) - 1
)

#free memory
rm(ul)
gc()

fit <- drbart(y, x, nburn=nburn, nsim=nsim, nthin=nthin,
              variance='ux', printevery=1,
              mean_cuts=c(enc2, enc3)
)
write_json(fit$fit$ucuts, path = "ucuts.json")
write_json(fit$fit$phistar, path = "phistar.json")
write_json(enc, path = "encoding.json")
write_json(c(x_values_categorical, x_values_continous), path = 'x_variables.json')
