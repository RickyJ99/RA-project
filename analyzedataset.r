setwd(getwd())
data <- read.csv("Extraction.csv", header = TRUE)
View(data)
attach(data)
result <- sum(nchar(QA) > 0)
result
my_data_truncated <- data
my_data_truncated$Main.text <- substr(my_data_truncated$Main.text, 1, 50)
View(my_data_truncated)
