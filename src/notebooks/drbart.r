library(cleandata)
library(devtools)
library(jsonlite)
devtools::install_github('ltsstar/drbart', ref = 'main')
library(drbart)

#load_all('~/Documents/drbart')
#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")


df <- read.csv('./artificial_start_end_2.csv')

x_values <- c('org.resource', 'concept.name')
y_value <- 'duration_seconds'



#
# STATIC PART
#

df_xy = na.omit(
  df[,c(x_values, y_value)]
)

enc <- lapply(x_values, function(x_value) {unique(df_xy[,x_value])})

df_xy <- apply(df_xy, 2, function(x) {as.numeric(factor(x, levels = unique(x)))})


x <- df_xy[, colnames(df_xy) != y_value]
y <- df_xy[, 'duration_seconds']

enc2 <- lapply(enc, function(v) {as.numeric(labels(v))})

fit <- drbart(y, x, nburn=100, nsim=10, nthin=10,
              variance='ux',
              mean_cuts=enc2
)
write_json(fit$fit$ucuts, path = "ucuts.json")
write_json(fit$fit$phistar, path = "phistar.json")
write_json(enc, path = "encoding.json")
