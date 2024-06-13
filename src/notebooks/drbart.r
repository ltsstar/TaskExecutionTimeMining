library(drbart)
df <- read.csv('./bpic_clean.csv')

df_xy = na.omit(
  df[,c('org.resource', 'concept.name', 'case.AMOUNT_REQ_start', 'duration_seconds')]
)

x <- data.matrix(df_xy[, names(df_xy) != 'duration_seconds'])
y <- df_xy[, 'duration_seconds']


fit <- drbart(y, x, m_mean=100)
