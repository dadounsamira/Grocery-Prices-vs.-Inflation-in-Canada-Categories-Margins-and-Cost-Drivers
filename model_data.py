# Build the modeling table for RQ3 (CIND820 Milestone 3)
from pathlib import Path
import pandas as pd

CLEAN = Path("data/clean")

# ===== Block A: the target y(t) =====
cpi = pd.read_csv(CLEAN / "cpi_clean.csv")
food = cpi[(cpi["GEO"] == "Canada") & (cpi["Group"] == "Food purchased from stores")]
food = food[["REF_DATE", "VALUE"]].rename(columns={"REF_DATE": "month", "VALUE": "food_cpi"})
food = food.sort_values("month").set_index("month")
food["y"] = food["food_cpi"].pct_change() * 100
print(food.head(3))
print(food["y"].describe().round(2))

# ===== Block B: drivers as lagged features =====
drivers = pd.read_csv(CLEAN / "drivers_monthly.csv").set_index("month").sort_index()
table = food.join(drivers)

changes = table[["energy_index", "agri_index", "usdcad"]].pct_change(12) * 100
changes["policy_rate"] = table["policy_rate"]

LAGS = [1, 3, 6, 9, 12, 15, 18]
for driver in ["agri_index", "energy_index", "usdcad", "policy_rate"]:
    for lag in LAGS:
        table[f"{driver}_lag{lag}"] = changes[driver].shift(lag)

print(table.shape)
print(table[["y", "agri_index_lag9", "energy_index_lag12"]].tail(3))

# ===== Block C: calendar months and events =====
month_number = table.index.str[5:7].astype(int)
months = pd.get_dummies(month_number, prefix="m", drop_first=True, dtype=int)
months.index = table.index
table = table.join(months)

table["covid"] = ((table.index >= "2020-03") & (table.index <= "2020-06")).astype(int)
table["ukraine"] = ((table.index >= "2022-02") & (table.index <= "2022-12")).astype(int)

print(table[["m_2", "m_12", "covid", "ukraine"]].loc["2020-02":"2020-07"])
print("Covid months:", table["covid"].sum(), "| Ukraine months:", table["ukraine"].sum())

# ===== Block D: keep complete rows, verify, save =====
lag_columns = [c for c in table.columns if "_lag" in c]
columns = ["y"] + lag_columns + list(months.columns) + ["covid", "ukraine"]
model_table = table[columns].dropna()

print("Model table:", model_table.shape)
print("From", model_table.index.min(), "to", model_table.index.max())
print("Missing values:", model_table.isna().sum().sum())

model_table.to_csv(CLEAN / "model_table.csv")
print("Saved: data/clean/model_table.csv")