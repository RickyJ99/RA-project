setwd("/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/")

data <- read.csv("/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/Data/6_TrumpwithCohmetrix.csv", header = TRUE)
View(data)
attach(data)
result <- sum(nchar(QA) > 0)
result
my_data_truncated <- data
my_data_truncated$Main.text <- substr(my_data_truncated$Main.text, 1, 50)
View(my_data_truncated)
head(data["Date.Time"])
is.Na

# Trump adm
# Filter data frame by Administration and Title
df <- data[data$Administration == "Trump", ] # & grepl('Press Briefing', data$Title), ]

df$UI_norm <- scale(df$UI) # scaling
install.packages(c("xts", "zoo", "MultipleBubbles", "aTSA", "urca", "flexmix", "forecast", "vars", "ggplot2", "knitr", "erer"))

library(xts)
library(zoo)
library(MultipleBubbles)
library(aTSA)
library(urca)
library(flexmix)
library(forecast)
library(vars)
library(ggplot2)
library(knitr)
library(erer)

# function
adf_test <- function(timeseries) { # nolint

    out <- matrix(NA, nrow = 0, ncol = 7)

    out_colnames <- c(
        "N of lags", "Type", "lag", "ADF",
        "p.value", "Stationary at 5%", "Stationary at 10%"
    )

    colnames(out) <- out_colnames

    for (count in 1:5) {
        i <<- adf.test(timeseries, output = FALSE)

        for (count2 in 1:3) {
            for (count3 in 1:count) {
                if (count2 == 1) {
                    rw <- c(
                        count, count2, count3,
                        i$type1[count3, 2], i$type1[count3, 3], NA, NA
                    )
                } else if (count2 == 2) {
                    rw <- c(
                        count, count2, count3,
                        i$type2[count3, 2], i$type2[count3, 3], NA, NA
                    )
                } else {
                    rw <- c(
                        count, count2, count3,
                        i$type3[count3, 2], i$type3[count3, 3], NA, NA
                    )
                }
                names(rw) <- out_colnames
                rw[1] <- as.integer(rw[1])
                rw[2] <- as.integer(rw[2])
                rw[3] <- as.integer(rw[3])
                rw["ADF"] <- round(rw["ADF"], digits = 4)
                rw["p.value"] <- round(rw["p.value"], digits = 4)
                if (rw["p.value"] >= .05) {
                    rw[6] <- "No Stat."
                } else {
                    rw[6] <- "Stat"
                }

                if (rw["p.value"] >= .1) {
                    rw[7] <- "No Stat."
                } else {
                    rw[7] <- "Stat"
                }
                if (rw["Type"] == 1) {
                    rw["Type"] <- "no drift no trend"
                } else if (rw["Type"] == 2) {
                    rw["Type"] <- "with drift no trend"
                } else {
                    rw["Type"] <- "with drift and trend"
                }
                out <- rbind(out, rw)
            }
        }
    }

    return(out)
}
time_series_plot <- function(timeseries) {
    out1 <- plot(timeseries)
    out2 <- acf(timeseries)
    out3 <- pacf(timeseries)
    # Stationarity
    out4 <- ur.df(timeseries,
        type = "drift",
        lags = 12, selectlags = "BIC"
    )
    out5 <- ur.df(timeseries,
        type = "trend",
        lags = 12, selectlags = "BIC"
    )
    out6 <- ur.df(timeseries,
        type = "none",
        lags = 12, selectlags = "BIC"
    )
    out7 <- adf_test(timeseries)
    out <- list(out1, out2, out3, out4, out5, out6, out7)
    return(out)
}
bic_score <- function(k, n, l) {
    x <- k * log(n) - 2 * l
    return(x)
}

# best arima select with BIC
bestarima <- function(timeseries, maxlag) {
    plag <- 1:maxlag
    qlag <- 1:maxlag

    model1 <- matrix(NA, nrow = 0, ncol = 3)
    colnames(model1) <- c("p", "q", "BIC")
    for (p in plag) {
        for (q in qlag) {
            out <- tryCatch(
                {
                    # Just to highlight: if you want to use more than one
                    # R expression in the "try" part then you'll have to
                    # use curly brackets.
                    # 'tryCatch()' will return the last evaluated expression
                    # in case the "try" part was completed successfully

                    arima(timeseries, order = c(p, 0, q))
                    # The return value of `readLines()` is the actual value
                    # that will be returned in case there is no condition
                    # (e.g. warning or error).
                    # You don't need to state the return value via `return()` as code
                    # in the "try" part is not wrapped inside a function (unlike that
                    # for the condition handlers for warnings and error below)
                },
                error = function(cond) {
                    # Choose a return value in case of error
                    return(NA)
                },
                warning = function(cond) {
                    # Choose a return value in case of warning
                    return(NA)
                }
            )
            if (any(!is.na(out))) {
                x <- arima(timeseries, order = c(p, 0, q))
                x_bic <- bic_score(length(x$coef), x$nobs, x$loglik)
            } else {
                x_bic <- 9999
            }
            model1 <- rbind(model1, c(p, q, x_bic))
        }
    }
    p <- model1[which.min(model1[, "BIC"]), "p"]
    q <- model1[which.min(model1[, "BIC"]), "q"]
    out <- arima(timeseries, order = c(p, 0, q))
    acf(out$residuals)
    return(c(p, 0, q))
}

# import dataser

# convert to xts


# Point 1

# generate xts







# Convert Date.Time to a POSIXct object
df$Date.Time <- as.POSIXct(df$Date.Time, format = "%Y-%m-%d %H:%M:%S")

l_yq <- length(df$Date.Time)
# Convert data frame to xts object
df_xts <- xts(df[, c("sentiment_score", "UI_norm")], order.by = df$Date.Time)
df_subset <- subset(df_xts, index(df_xts) > as.POSIXct("2020-01-01") & index(df_xts) < as.POSIXct("2021-09-01"))

# Plot time series of sentiment_score and UI

plot(df_subset[, 1], type = "l", col = "#0077ff", xlab = "Date", ylab = "Sentiment Score")
lines(df_subset[, 2], col = "#ff00a2")
legend("topright", legend = c("Sentiment Score", "UI"), col = c("#0077ff", "#ff00a2"), lty = 1:1, cex = 1)
title(main = "Time Series of Sentiment Score and UI")




timeseries <- ts(df_xts$sentiment_score)
out <- time_series_plot(timeseries)


kable(out[[7]])

print("Without constant and without time trend")
print(out[[6]])
# plot(out[[6]])
print("With constant and without time trend")
print(out[[4]])
# plot(out[[4]])
print("With constant and with time trend")
print(out[[5]])
# plot(out[[5]])











# Function calculating the BIC score

bic_score <- function(k, n, l) {
    x <- 2 * k * log(n) - 2 * l
    return(x)
}

# Best arima model selected with the BIC criterion
bestarima <- function(timeseries, maxlag) {
    plag <- 1:maxlag
    qlag <- 1:maxlag

    model1 <- matrix(NA, nrow = 0, ncol = 3)
    colnames(model1) <- c("p", "q", "BIC")
    for (p in plag) {
        for (q in qlag) {
            out <- tryCatch(
                {
                    # Just to highlight: if you want to use more than one
                    # R expression in the "try" part then you'll have to
                    # use curly brackets.
                    # 'tryCatch()' will return the last evaluated expression
                    # in case the "try" part was completed successfully

                    arima(timeseries, order = c(p, 0, q))
                    # The return value of `readLines()` is the actual value
                    # that will be returned in case there is no condition
                    # (e.g. warning or error).
                    # You don't need to state the return value via `return()` as code
                    # in the "try" part is not wrapped inside a function (unlike that
                    # for the condition handlers for warnings and error below)
                },
                error = function(cond) {
                    # Choose a return value in case of error
                    return(NA)
                },
                warning = function(cond) {
                    # Choose a return value in case of warning
                    return(NA)
                }
            )
            if (any(!is.na(out))) {
                x <- arima(timeseries, order = c(p, 0, q))
                x_bic <- bic_score(length(x$coef), x$nobs, x$loglik)
            } else {
                x_bic <- 9999
            }
            model1 <- rbind(model1, c(p, q, x_bic))
        }
    }
    p <- model1[which.min(model1[, "BIC"]), "p"]
    q <- model1[which.min(model1[, "BIC"]), "q"]
    out <- arima(timeseries, order = c(p, 0, q))
    acf(out$residuals)
    return(c(p, 0, q))
}

best_arima <- bestarima(timeseries, 4)

arma <- arima(timeseries, order = best_arima, method = "ML")
print(paste("BIC:", bic_score(length(arma$coef), arma$nobs, arma$loglik)))
summary(arma)
plot(arma)
plot(acf(arma$residuals))
plot(pacf(arma$residuals))

# table with just R output
# Test stationarity
acf(df_xts$UI)



# bic_score(length(arma$coef), arma$nobs, arma$loglik))

# estimation
var_model_lev <- VAR(df_xts, lag.max = 3, type = "const", ic = "HQ")
res <- residuals(var_model_lev)
par(mfrow = c(1, 1))
acf(res[, 1])
acf(res[, 2])


par(mfrow = c(1, 1))
pacf(res[, 1])
pacf(res[, 2])


# Calculate summary statistics
model_summary <- summary(var_model_lev)
model_summary

# Obtain variance-covariance matrix
model_summary$covres
model_summary$corres

invroots <- roots(var_model_lev, modulus = FALSE) # no stationary

par(mfrow = c(1, 1))
root.comp <- Im(invroots)
root.real <- Re(invroots)
x <- seq(-1, 1, length = 1000)
y1 <- sqrt(1 - x^2)
y2 <- -sqrt(1 - x^2)
plot(c(x, x), c(y1, y2), xlab = "Immaginary part", ylab = "Real part", type = "l", main = "Unit Circle", ylim = c(-2, 2), xlim = c(-2, 2))
abline(h = 0)
abline(v = 0)
points(root.real, root.comp, pch = 19)
legend(-1.5, -1.5, legend = "Eigenvalues", pch = 19)
oir <- irf(var_model_lev,
    impulse = colnames(df_xts)[1],
    response = colnames(df_xts)[2], n.ahead = 25,
    ortho = TRUE, runs = 100, seed = 12345
)
plot(oir)
oir <- irf(var_model_lev,
    impulse = colnames(df_xts)[1],
    response = colnames(df_xts)[1], n.ahead = 25,
    ortho = TRUE, runs = 1000, seed = 12345
)
plot(oir)
oir <- irf(var_model_lev,
    impulse = colnames(df_xts)[2],
    response = colnames(df_xts)[2], n.ahead = 25,
    ortho = TRUE, runs = 100, seed = 12345
)
plot(oir)
oir <- irf(var_model_lev,
    impulse = colnames(df_xts)[2],
    response = colnames(df_xts)[1], n.ahead = 25,
    ortho = TRUE, runs = 100, seed = 12345
)
plot(oir)
