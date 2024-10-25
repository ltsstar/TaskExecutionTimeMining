
input <- file("stdin")

df <- read.csv(input, header=TRUE)
#names(df) <- make.names(names(df), unique = TRUE)
str_names <- paste0('\'', paste(names(df), collapse = '\', \''), '\'\n')
cat(str_names)
