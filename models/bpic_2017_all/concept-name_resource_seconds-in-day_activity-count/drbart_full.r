#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/BPIC_2017_all_train.csv'

x_values_categorical <- c('org.resource_start', 'concept.name',
			  'W_Assess.potential.fraud__ate_abort', 'W_Assess.potential.fraud__complete', 'W_Assess.potential.fraud__resume', 'W_Assess.potential.fraud__schedule', 'W_Assess.potential.fraud__start', 'W_Assess.potential.fraud__suspend', 'W_Assess.potential.fraud__withdraw', 'W_Call.after.offers__ate_abort', 'W_Call.after.offers__complete', 'W_Call.after.offers__resume', 'W_Call.after.offers__schedule', 'W_Call.after.offers__start', 'W_Call.after.offers__suspend', 'W_Call.after.offers__withdraw', 'W_Call.incomplete.files__ate_abort', 'W_Call.incomplete.files__complete', 'W_Call.incomplete.files__resume', 'W_Call.incomplete.files__schedule', 'W_Call.incomplete.files__start', 'W_Call.incomplete.files__suspend', 'W_Complete.application__ate_abort', 'W_Complete.application__complete', 'W_Complete.application__resume', 'W_Complete.application__schedule', 'W_Complete.application__start', 'W_Complete.application__suspend', 'W_Handle.leads__complete', 'W_Handle.leads__resume', 'W_Handle.leads__schedule', 'W_Handle.leads__start', 'W_Handle.leads__suspend', 'W_Handle.leads__withdraw', 'W_Shortened.completion.__resume', 'W_Shortened.completion.__schedule', 'W_Shortened.completion.__start', 'W_Shortened.completion.__suspend', 'W_Validate.application__ate_abort', 'W_Validate.application__complete', 'W_Validate.application__resume', 'W_Validate.application__schedule', 'W_Validate.application__start', 'W_Validate.application__suspend'
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
