library(cleandata)
library(devtools)
library(jsonlite)
devtools::install_github('ltsstar/drbart', ref = 'main')
library(drbart)

#load_all('~/Documents/drbart')
#setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")

df <- read.csv('../../kernel_all.csv')

df_xy = na.omit(
  df[,c(
    'seconds_of_day',
    'org.resource_left',
    'concept.name_left',
    'duration_seconds_left'
    )]
)

#write.csv(na.omit(df), 'celonis.csv')
#df_xy = subset(df_xy, case.AMOUNT_REQ_complete > 10000)
df_xy$org.resource_left <- factor(df_xy$org.resource_left,
                             levels = unique(df$org.resource_left))
df_xy$concept.name_left <- factor(df_xy$concept.name_left,
                             levels = unique(df$concept.name_left))
x <- data.matrix(df_xy[, names(df_xy) != 'duration_seconds_left'])
y <- df_xy[, 'duration_seconds_left']



fit <- drbart(y, x, nburn=10000, nsim=1000, nthin=10,
              variance='ux',# alpha = 0.5, beta = 0.5,
              mean_cuts=list(
                seq(
                        min(df_xy$seconds_of_day),
                        max(df_xy$seconds_of_day),
                        length.out=min(
                                10000,
                                length(unique(df_xy$seconds_of_day))
                        )
                ),
		unique(df_xy$org.resource_left),
                unique(df_xy$concept.name_left)
              )
)
write_json(fit$fit$ucuts, path = "ucuts.json")
write_json(fit$fit$phistar, path = "phistar.json")


