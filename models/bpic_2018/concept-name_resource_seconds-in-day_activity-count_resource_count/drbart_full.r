#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2018_start_end_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name_start',
			  'abort.external', 'abort.payment', 'approve', 'begin.admissibility.check', 'begin.editing', 'begin.editing.from.refused', 'begin.payment', 'begin.preparations', 'calculate', 'calculate.protocol', 'cancel.offline', 'change.department', 'check', 'check.admissibility', 'clear', 'correction.GFM17', 'create', 'decide', 'discard', 'finish.editing', 'finish.payment', 'finish.pre.check', 'finish.preparations', 'initialize', 'insert.document', 'mail.income', 'mail.valid', 'performed', 'performed.offline', 'plan', 'prepare.external', 'prepare.offline', 'refuse', 'remove.document', 'restart.editing', 'revoke.approval', 'revoke.decision', 'revoke.withdrawal', 'save', 'take.original.document', 'withdraw', 'X00037f', 'X0087cf', 'X019209', 'X023bb9', 'X03b214', 'X059abc', 'X07361d', 'X08e484', 'X0.n.a', 'X0d884f', 'X0fe39b', 'X13c937', 'X155add', 'X167893', 'X1bd3b5', 'X1c1894', 'X2044b6', 'X21612d', 'X237892', 'X27cc37', 'X28b6bf', 'X2ac4ac', 'X2b8616', 'X2baab0', 'X2bf205', 'X2c546f', 'X2ca0ae', 'X2dc625', 'X313338', 'X346f05', 'X352a49', 'X354865', 'X36c75c', 'X39be3e', 'X3d952e', 'X40178c', 'X425ee3', 'X4298e3', 'X439089', 'X44798d', 'X465290', 'X46e3af', 'X478c4f', 'X483029', 'X4af6fb', 'X4b9a7f', 'X4e9bc2', 'X4fac6d', 'X51d239', 'X520882', 'X556da9', 'X5a21a5', 'X5bf77a', 'X5c1b3c', 'X5d8173', 'X5d9e09', 'X5dd4ec', 'X5e018b', 'X60b0b8', 'X65bf34', 'X6ad4a6', 'X6c720c', 'X6d6ae5', 'X6f6a4e', 'X6fde6b', 'X7078c7', 'X71ffe8', 'X727350', 'X75992a', 'X76f30e', 'X7850e8', 'X7886b1', 'X79367e', 'X796771', 'X7b9b55', 'X7d03a0', 'X7d12ba', 'X7d4a25', 'X7fb8a5', 'X815d19', 'X822fb7', 'X82518f', 'X83c7b7', 'X8a1fba', 'X8aab8f', 'X8beb64', 'X8c9a01', 'X8d8538', 'X91bca0', 'X9765da', 'X97d224', 'X99e048', 'X9aaf68', 'X9e088c', 'X9e337f', 'DP.R', 'DP.Z', 'Document.processing.automaton', 'Inspection.automaton', 'Inspection.service', 'Notification.automaton', 'Parcel.automaton', 'Processing.automaton', 'Reference.alignment.processor', 'Remote.inspection.export', 'Remote.inspection.import', 'a21e1b', 'a5ae3f', 'a5c3dd', 'abe845', 'ad25fc', 'aea7c8', 'af1e1e', 'b2b786', 'b33ed5', 'b4755f', 'b90293', 'ba978b', 'bbd307', 'bc063d', 'bfa0ec', 'c0aa4a', 'c39cb2', 'c4f075', 'c522f8', 'c70c37', 'c70d79', 'c7c478', 'c966f4', 'c98a4a', 'd0f451', 'd114c8', 'd4758f', 'd4d37d', 'd85681', 'd8639c', 'dd04e2', 'dd12cf', 'dde669', 'dee71b', 'dfd1d4', 'e25f20', 'e99397', 'ea52aa', 'eb38eb', 'eb7015', 'ee262f', 'ee28de', 'ef80e3', 'f01c35', 'f3e81e', 'f48280', 'f6846a', 'f6f7f1', 'f7f7b6', 'f8da29', 'f9fe07', 'fa6437', 'fa68d2', 'fb5fa8', 'fc6177', 'fcb55b', 'ffb56b', 'parcel.correction.automaton', 'scheduler'
		 	  )
x_values_continous <- c(#'case.RequestedAmount_suspend',
			'seconds_in_day')
y_value <- 'duration_seconds'


nburn <- 25000
nsim <- 150
nthin <- 150



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
