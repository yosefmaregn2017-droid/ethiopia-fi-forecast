# task4_forecasting.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# 1️⃣ Paths and directories
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "ethiopia_fi_unified_data.xlsx"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

REPORTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# -----------------------------
# 2️⃣ Load data
# -----------------------------
fi_data = pd.read_excel(RAW_DATA_PATH)

# Convert observation_date to datetime
fi_data['observation_date'] = pd.to_datetime(fi_data['observation_date'], errors='coerce')

# Filter numeric observations only
obs = fi_data[fi_data['value_numeric'].notna()].copy()
obs = obs.rename(columns={'observation_date': 'date'})
obs['indicator_code'] = obs['indicator_code'].astype(str)

print(f"Observations loaded: {len(obs)}")

# -----------------------------
# 3️⃣ Forecasting (placeholder: simple moving average)
# -----------------------------
forecast_horizon = 3  # months/periods ahead
forecast_results = []

unique_indicators = obs['indicator_code'].unique()

for ind in unique_indicators:
    ind_data = obs[obs['indicator_code'] == ind].sort_values('date')
    if len(ind_data) < 3:
        print(f"Not enough data for {ind}, skipping...")
        continue
    
    ind_data['forecast'] = ind_data['value_numeric'].rolling(window=3, min_periods=1).mean().shift(1)
    
    forecast_results.append(ind_data[['date', 'indicator_code', 'value_numeric', 'forecast']])

# Concatenate all forecast results
forecast_df = pd.concat(forecast_results, ignore_index=True)
forecast_csv_path = REPORTS_DIR / "forecast_results.csv"
forecast_df.to_csv(forecast_csv_path, index=False)
print(f"Forecast results saved: {forecast_csv_path}")

# -----------------------------
# 4️⃣ Plot forecasts
# -----------------------------
for ind in unique_indicators:
    ind_data = forecast_df[forecast_df['indicator_code'] == ind]
    if ind_data.empty:
        continue

    plt.figure(figsize=(10,5))
    plt.plot(ind_data['date'], ind_data['value_numeric'], label='Actual', marker='o')
    plt.plot(ind_data['date'], ind_data['forecast'], label='Forecast', marker='x')
    plt.title(f"Forecast for {ind}")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    fig_path = FIGURES_DIR / f"{ind}_forecast.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"Saved figure: {fig_path}")

print("✅ Task 4 forecasting completed successfully!")
