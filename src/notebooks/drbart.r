library(devtools)
devtools::install_github('ltsstar/drbart', ref = 'main')
library(drbart)
df <- read.csv('./bpic_clean.csv')

df_xy = na.omit(
  df[,c('org.resource', 'concept.name', 'case.AMOUNT_REQ_start', 'duration_seconds')]
)
df_xy$org.resource <- factor(df_xy$org.resource)
df_xy$concept.name <- factor(df_xy$concept.name)
x <- as.matrix(
  data.matrix(
  df_xy[, names(df_xy) != 'duration_seconds']
),
ncol=3)
y <- df_xy[, 'duration_seconds']
dim(x)

fit <- drbart(y, x, nburn=10000, nsim=100000)
saveRDS(fit, "model2.rds")

x_pred <- as.matrix(
  data.matrix(
    data.frame(org.resource <- unique(df_xy['org.resource'])[['org.resource']][1:25],
               concept.name <- c(2),
               case.AMOUNT_REQ_start <- c(20000)
    )
),
ncol=3)

#ygrid <- matrix(rep(seq(0, 5000, length.out=2500), 2),
#                nrow=2, ncol=2500, byrow=T)
ygrid <- seq(0, 500, length.out=250)
pred <- predict(fit,
                x_pred, ygrid)
plot(pred)
#list(x = xpred, y = ygrid, sample = seq_len(dim(preds)[3])) 

  