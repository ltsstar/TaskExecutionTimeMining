library(cleandata)
library(devtools)
load_all('~/Documents/drbart')
setwd("~/Documents/TaskExecutionTimeMining/src/notebooks")

df <- read.csv('./bpic_clean.csv')

df_xy = na.omit(
  df[,c(
    'case.AMOUNT_REQ_complete',
    'org.resource',
    'concept.name',
    'duration_seconds'
    )]
)

write.csv(na.omit(df), 'celonis.csv')
#df_xy = subset(df_xy, case.AMOUNT_REQ_complete > 10000)
df_xy$org.resource <- factor(df_xy$org.resource,
                             levels = unique(df$org.resource))
df_xy$concept.name <- factor(df_xy$concept.name,
                             levels = unique(df$concept.name))
x <- data.matrix(df_xy[, names(df_xy) != 'duration_seconds'])
y <- df_xy[, 'duration_seconds']



fit <- drbart(y, x, nburn=20, nsim=2, nthin=2,
              m_mean=4,
              m_var=4,
              variance='ux',# alpha = 0.5, beta = 0.5,
              mean_cuts=list(
                seq(
                  min(df_xy$case.AMOUNT_REQ_complete),
                  max(df_xy$case.AMOUNT_REQ_complete),
                  length.out=min(
                    10000,
                    length(unique(df_xy$case.AMOUNT_REQ_complete))
                  )),
                unique(df_xy$org.resource),
                unique(df_xy$concept.name)
              )
)

concept_pred <- factor(c('W_Afhandelen leads', 'W_Afhandelen leads'
                         ),
                       levels = unique(df$concept.name))
resource_pred <- factor(c(10228, 10228),
                        levels = unique(df$org.resource))

x_pred <- as.matrix(
  data.matrix(
    data.frame(case.AMOUNT_REQ_start <- c(400000, 1000),
               org.resource <- resource_pred,
               concept.name <- concept_pred
               #concept.name <- concept_pred,
    )
  ),
  ncol=3)


ygrid <- seq(0, 500, length.out=20)
load_all('~/Documents/drbart')
pred <- predict(fit, x_pred, ygrid)
plot(pred)

