import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Importing data
Trump = pd.read_csv(
    "/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/Data/5_TrumpwithCohmetrix.csv"
)

# Convert the string column to datetime
Trump["Date Time"] = pd.to_datetime(
    Trump["Date Time"], format="%Y-%m-%d %H:%M:%S%z"
).dt.tz_localize(None)
Trump = Trump.iloc[1:]  # eliminate the first row containing the title

# Setting as time index
Trump = Trump.set_index("Date Time")

# Assuming X and DateTime are already defined
X = Trump["SYNLE"]

# Convert DateTime to a datetime array
DateTime = pd.to_datetime(Trump.index.date)

# Define the start and end dates for each week
startWeek = pd.date_range(start=min(DateTime), end=max(DateTime), freq="7D")
endWeek = startWeek + timedelta(days=6)

# Initialize arrays to store weekly averages and corresponding dates
weeklyAverages = np.zeros(len(startWeek))
weeklyDates = startWeek

# Calculate weekly averages
for i in range(len(startWeek)):
    # Find indices of observations within the current week
    weekIndices = (DateTime >= startWeek[i]) & (DateTime <= endWeek[i])

    # Calculate the average of X within the current week
    weeklyAverages[i] = np.mean(X[weekIndices])

X_weekly = weeklyAverages

# Display the weekly averages and corresponding dates
print("Weekly Averages:")
print(weeklyAverages)
print("Dates:")
print(weeklyDates)

# Plot the weekly averages
import matplotlib.pyplot as plt

plt.plot(weeklyDates, weeklyAverages)
plt.show()

Y = Trump["sentiment_score"]

# Calculate weekly averages for Y
for i in range(len(startWeek)):
    # Find indices of observations within the current week
    weekIndices = (DateTime >= startWeek[i]) & (DateTime <= endWeek[i])

    # Calculate the average of Y within the current week
    weeklyAverages[i] = np.mean(Y[weekIndices])

Y_weekly = weeklyAverages

Z = Trump["UI"]

# Calculate weekly averages for Z
for i in range(len(startWeek)):
    # Find indices of observations within the current week
    weekIndices = (DateTime >= startWeek[i]) & (DateTime <= endWeek[i])

    # Calculate the average of Z within the current week
    weeklyAverages[i] = np.mean(Z[weekIndices])

Z_weekly = weeklyAverages

# Create the output timetable
output_data = {"EPU": Z_weekly, "SYN": X_weekly, "Sent": Y_weekly}
Z = pd.DataFrame(output_data, index=weeklyDates)

# Write the output to a CSV file
Z.to_csv("output.csv")
