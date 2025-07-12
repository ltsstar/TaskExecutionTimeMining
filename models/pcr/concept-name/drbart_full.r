#
# DYNAMIC PART
#

#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


file_location <- '../../../src/notebooks/transformed_event_logs/PCR_start_end_train.csv'

x_values_categorical <- c('concept.name')
x_values_continous <- c(#'case.RequestedAmount_suspend',
			#'seconds_in_day'
)
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
