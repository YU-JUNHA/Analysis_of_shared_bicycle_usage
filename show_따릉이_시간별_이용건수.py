import pandas as pd
import matplotlib.pyplot as plt

# Read CSV
df = pd.read_csv("따릉이_시간별_이용건수.csv", encoding="utf-8-sig")

# Choose y column (file may have either)
ycol = "avg_daily_rides" if "avg_daily_rides" in df.columns else "total_rides"

# Sort by hour
df = df.sort_values("hour")

# Bar chart
ax = df.set_index("hour")[ycol].plot(
    kind="bar",
    title="Average Rides by Hour",
    figsize=(9, 4)
)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Average Rides")
plt.tight_layout()

# Show (or save)
plt.show()
# plt.savefig("rides_by_hour_bar.png", dpi=150)