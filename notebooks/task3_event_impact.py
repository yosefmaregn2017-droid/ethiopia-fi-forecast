import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Load Data
# -----------------------------
fi_data = pd.read_excel("data/raw/ethiopia_fi_unified_data.xlsx")

fi_data["observation_date"] = pd.to_datetime(
    fi_data["observation_date"], errors="coerce"
)

# -----------------------------
# Split Data
# -----------------------------
events = fi_data[fi_data["record_type"] == "event"]
observations = fi_data[fi_data["record_type"] == "observation"]

print("Events:", len(events))
print("Observations:", len(observations))


# -----------------------------
# Function: Impact Analysis
# -----------------------------
def analyze_impact(event_code, indicator_code, window=2):
    """
    Compare indicator before and after event
    window = years before/after
    """

    event = events[events["indicator_code"] == event_code]

    if event.empty:
        print(f"No event found: {event_code}")
        return None

    event_date = event["observation_date"].iloc[0]

    indicator = observations[
        observations["indicator_code"] == indicator_code
    ].copy()

    indicator = indicator.sort_values("observation_date")

    # Before & After Windows
    before = indicator[
        (indicator["observation_date"] < event_date) &
        (indicator["observation_date"] >= event_date - pd.DateOffset(years=window))
    ]

    after = indicator[
        (indicator["observation_date"] > event_date) &
        (indicator["observation_date"] <= event_date + pd.DateOffset(years=window))
    ]

    if before.empty or after.empty:
        print(f"Not enough data for {event_code}")
        return None

    before_avg = before["value_numeric"].mean()
    after_avg = after["value_numeric"].mean()

    change_pct = ((after_avg - before_avg) / before_avg) * 100

    return {
        "Event": event_code,
        "Indicator": indicator_code,
        "Before Avg": round(before_avg, 2),
        "After Avg": round(after_avg, 2),
        "Change (%)": round(change_pct, 2)
    }


# -----------------------------
# Analyze Major Events
# -----------------------------
results = []

pairs = [
    ("EVT_TELEBIRR", "USG_TELEBIRR_USERS"),
    ("EVT_MPESA", "USG_MPESA_USERS"),
    ("EVT_FAYDA", "ACC_FAYDA"),
    ("EVT_SAFARICOM", "USG_MOBILE_PEN")
]

for event, indicator in pairs:
    res = analyze_impact(event, indicator)

    if res:
        results.append(res)


# -----------------------------
# Results Table
# -----------------------------
impact_df = pd.DataFrame(results)

print("\nEvent Impact Summary:")
print(impact_df)


# -----------------------------
# Save Results
# -----------------------------
import os

os.makedirs("reports", exist_ok=True)

impact_df.to_csv(
    os.path.join("reports", "event_impact_results.csv"),
    index=False
)


print("\nSaved: reports/event_impact_results.csv")


# -----------------------------
# Visualization
# -----------------------------
# -----------------------------
# Plot Only If Data Exists
# -----------------------------
if not impact_df.empty:

    impact_df.plot(
        x="Event",
        y="Change (%)",
        kind="bar",
        title="Event Impact on Financial Indicators"
    )

    plt.ylabel("Percentage Change")
    plt.show()

else:
    print("\nNo sufficient data to plot event impacts.")
