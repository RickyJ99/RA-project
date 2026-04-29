import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

DATA_PATH = "Data/6_TrumpwithCohmetrix.csv"
OUTPUT_PATH = "Data/6_TrumpwithCohmetrix_freq.csv"

Trump = pd.read_csv(DATA_PATH)

# tz_convert(None) strips timezone info from tz-aware datetimes;
# tz_localize(None) would raise TypeError on already-aware series.
Trump["Date Time"] = pd.to_datetime(
    Trump["Date Time"], format="%Y-%m-%d %H:%M:%S%z"
).dt.tz_convert(None)

Trump = Trump.set_index("Date Time")

DateTime = pd.to_datetime(Trump.index.date)

startWeek = pd.date_range(start=DateTime.min(), end=DateTime.max(), freq="7D")
endWeek = startWeek + timedelta(days=6)

n_weeks = len(startWeek)
X_weekly = np.zeros(n_weeks)
Y_weekly = np.zeros(n_weeks)
Z_weekly = np.zeros(n_weeks)

X = Trump["SYNLE"]
Y = Trump["sentiment_score"]
Z = Trump["UI"]

for i in range(n_weeks):
    mask = (DateTime >= startWeek[i]) & (DateTime <= endWeek[i])
    X_weekly[i] = np.nanmean(X[mask])
    Y_weekly[i] = np.nanmean(Y[mask])
    Z_weekly[i] = np.nanmean(Z[mask])

print("Weekly Averages (SYNLE):")
print(X_weekly)
print("Dates:")
print(startWeek)

plt.figure()
plt.plot(startWeek, X_weekly)
plt.xlabel("Date")
plt.ylabel("SYNLE (weekly avg)")
plt.title("Syntactic complexity — weekly averages")
plt.tight_layout()
plt.show()

output = pd.DataFrame(
    {"EPU": Z_weekly, "SYN": X_weekly, "Sent": Y_weekly},
    index=startWeek,
)
output.to_csv(OUTPUT_PATH)
print(f"Saved weekly data → {OUTPUT_PATH}")
