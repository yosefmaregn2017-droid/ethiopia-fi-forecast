import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# -----------------------------
# Load data (adjust path if needed)
# -----------------------------
fi_data = pd.read_excel("data/raw/ethiopia_fi_unified_data.xlsx")

# -----------------------------
# 1. Overview
# -----------------------------
print("FI Data shape:", fi_data.shape)
print("\nRecords by type:\n", fi_data["record_type"].value_counts())

# -----------------------------
# 2. Convert date
# -----------------------------
fi_data["observation_date"] = pd.to_datetime(
    fi_data["observation_date"], errors="coerce"
)

# -----------------------------
# 3. Observations per year
# -----------------------------
obs = fi_data[fi_data["record_type"] == "observation"]

obs_counts = (
    obs.groupby(obs["observation_date"].dt.year)["record_id"]
    .count()
)

plt.figure()
obs_counts.plot(kind="bar")
plt.title("Observations per Year")
plt.xlabel("Year")
plt.ylabel("Count")
plt.show()

# -----------------------------
# 4. Account Ownership Trend
# -----------------------------
acc = fi_data[
    (fi_data["pillar"] == "ACCESS") &
    (fi_data["indicator_code"] == "ACC_OWNERSHIP")
]

plt.figure()
plt.plot(
    acc["observation_date"],
    acc["value_numeric"],
    marker="o"
)
plt.title("Account Ownership Over Time")
plt.xlabel("Year")
plt.ylabel("Percent")
plt.grid()
plt.show()

# -----------------------------
# 5. Digital Payment Usage
# -----------------------------
usage = fi_data[
    (fi_data["pillar"] == "USAGE") &
    (fi_data["indicator_code"].isin([
        "USG_TELEBIRR_USERS",
        "USG_MPESA_USERS"
    ]))
]

plt.figure()
for code in usage["indicator_code"].unique():
    temp = usage[usage["indicator_code"] == code]
    plt.plot(
        temp["observation_date"],
        temp["value_numeric"],
        marker="o",
        label=code
    )

plt.title("Digital Payment Usage")
plt.xlabel("Year")
plt.ylabel("Users")
plt.legend()
plt.grid()
plt.show()

# -----------------------------
# 6. Events Timeline
# -----------------------------
events = fi_data[fi_data["record_type"] == "event"]

plt.figure()
plt.scatter(
    events["observation_date"],
    [1]*len(events),
    color="red"
)

plt.title("Policy & Market Events")
plt.xlabel("Year")
plt.yticks([])
plt.show()

# -----------------------------
# 7. Confidence Distribution
# -----------------------------
if "confidence" in fi_data.columns:

    conf = fi_data["confidence"].value_counts()

    plt.figure()
    conf.plot(kind="bar")
    plt.title("Confidence Distribution")
    plt.xlabel("Level")
    plt.ylabel("Count")
    plt.show()

# -----------------------------
# 8. Summary Stats
# -----------------------------
print("\nSummary Statistics:")
print(
    fi_data.groupby("indicator_code")["value_numeric"]
    .describe()
)
