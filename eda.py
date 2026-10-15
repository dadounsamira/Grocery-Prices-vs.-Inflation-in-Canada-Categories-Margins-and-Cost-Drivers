# Exploratory data analysis (EDA) for CIND820 Milestone 2
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CLEAN = Path("data/clean")
EDA = Path("outputs/eda")
EDA.mkdir(parents=True, exist_ok=True)

# LOOK: load the 3 clean tables
cpi = pd.read_csv(CLEAN / "cpi_clean.csv")
retail = pd.read_csv(CLEAN / "retail_prices_clean.csv")
drivers = pd.read_csv(CLEAN / "drivers_monthly.csv")
for name, table in [("cpi", cpi), ("retail", retail), ("drivers", drivers)]:
    print(name, table.shape, "| columns:", list(table.columns))

# ===== Part 1 (RQ1): grocery food vs all-items, Canada, January 2019 = 100 =====
canada = cpi[(cpi["GEO"] == "Canada") & (cpi["REF_DATE"] >= "2019-01")]
wide = canada.pivot(index="REF_DATE", columns="Group", values="VALUE")
print("Wide table:", wide.shape)

rebased = wide / wide.iloc[0] * 100
print(rebased[["All-items", "Food purchased from stores"]].head(3))
print(rebased[["All-items", "Food purchased from stores"]].tail(1))

last = rebased.iloc[-1]
print("Gap in Aug 2026 (percentage points):", round(last["Food purchased from stores"] - last["All-items"], 1))

# Chart: two lines, both starting at 100 in January 2019
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(rebased.index, rebased["Food purchased from stores"], label="Food purchased from stores")
ax.plot(rebased.index, rebased["All-items"], label="All-items CPI")
ax.axhline(100, color="grey", linewidth=0.8)
ax.set_title("Grocery prices vs. overall inflation, Canada (January 2019 = 100)")
ax.set_ylabel("Index, January 2019 = 100")
ax.set_xticks(rebased.index[::12])
ax.legend()
fig.tight_layout()
fig.savefig(EDA / "01_food_vs_allitems_canada.png", dpi=150)
plt.show()


# ===== Part 2 (RQ1): change by food category, Canada, Jan 2019 -> Aug 2026 =====
CATEGORIES = ["Meat", "Fish, seafood and other marine products", "Dairy products and eggs",
              "Bakery and cereal products (excluding baby food)",
              "Fruit, fruit preparations and nuts", "Vegetables and vegetable preparations",
              "Other food products and non-alcoholic beverages"]
change = (rebased.iloc[-1][CATEGORIES] - 100).sort_values()
print(change.round(1))

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(change.index, change.values)
ax.axvline(rebased.iloc[-1]["All-items"] - 100, color="grey", linestyle="--", label="All-items CPI")
ax.set_title("Price change by food category, Canada, January 2019 to August 2026")
ax.set_xlabel("% change since January 2019")
ax.legend()
fig.tight_layout()
fig.savefig(EDA / "02_change_by_category_canada.png", dpi=150)
plt.show()

# ===== Part 3 (RQ1): store food vs all-items, by province, Jan 2019 -> Aug 2026 =====
start = cpi[cpi["REF_DATE"] == "2019-01"].pivot(index="GEO", columns="Group", values="VALUE")
end = cpi[cpi["REF_DATE"] == "2026-08"].pivot(index="GEO", columns="Group", values="VALUE")
pct = end / start * 100 - 100

prov = pct[["Food purchased from stores", "All-items"]].copy()
prov["gap_pp"] = prov["Food purchased from stores"] - prov["All-items"]
prov = prov.sort_values("gap_pp")
print(prov.round(1))

# Chart: gap by province (Canada in grey for reference)
colors = ["grey" if place == "Canada" else "tab:blue" for place in prov.index]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(prov.index, prov["gap_pp"], color=colors)
ax.set_title("Grocery inflation minus overall inflation, by province, Jan 2019 to Aug 2026")
ax.set_xlabel("Gap in percentage points (store food % change minus all-items % change)")
fig.tight_layout()
fig.savefig(EDA / "03_gap_by_province.png", dpi=150)
plt.show()

# Save the numbers too (for the report and Power BI)
prov.round(1).to_csv(EDA / "03_gap_by_province.csv")

# ===== Part 4 (RQ3): the 4 drivers over time, with 2 dated events =====
EVENTS = ["2020-03", "2022-02"]   # COVID-19 lockdowns, Russia invades Ukraine

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
panels = [(axes[0, 0], "energy_index", "Energy commodity index (1972 = 100)"),
          (axes[0, 1], "agri_index", "Agriculture commodity index (1972 = 100)"),
          (axes[1, 0], "usdcad", "USD/CAD (Canadian dollars per 1 US dollar)"),
          (axes[1, 1], "policy_rate", "Bank of Canada policy rate (%)")]

for ax, column, title in panels:
    ax.plot(drivers["month"], drivers[column])
    for month in EVENTS:
        ax.axvline(month, color="red", linestyle=":", linewidth=1)
    ax.set_title(title, fontsize=10)
    ax.set_xticks(drivers["month"][::24])

fig.suptitle("Possible drivers of food prices, 2017-2026 (red dotted lines: COVID-19, Ukraine war)")
fig.tight_layout()
fig.savefig(EDA / "04_drivers_over_time.png", dpi=150)
plt.show()

# ===== Part 5 (RQ3): relationships between food prices and the drivers =====
food = cpi[(cpi["GEO"] == "Canada") & (cpi["Group"] == "Food purchased from stores")]
food = food[["REF_DATE", "VALUE"]].rename(columns={"REF_DATE": "month", "VALUE": "food_cpi"})
both = food.merge(drivers, on="month").set_index("month")
print("Joined:", both.shape)

changes = both[["food_cpi", "energy_index", "agri_index", "usdcad"]].pct_change(12) * 100
changes["policy_rate"] = both["policy_rate"]
changes = changes.dropna()
print(changes.round(1).head(3))
print("Months with a year-over-year change:", len(changes))

# Correlation between food inflation and each driver, with the driver shifted back 0-12 months
LAGS = [0, 3, 6, 9, 12, 15, 18, 24]
DRIVERS = ["energy_index", "agri_index", "usdcad", "policy_rate"]

lag_table = pd.DataFrame(index=LAGS, columns=DRIVERS, dtype=float)
for driver in DRIVERS:
    for lag in LAGS:
        lag_table.loc[lag, driver] = changes["food_cpi"].corr(changes[driver].shift(lag))

lag_table.index.name = "lag (months)"
print(lag_table.round(2))
lag_table.round(2).to_csv(EDA / "05_lag_correlations.csv")

# Chart: correlation with food inflation, by lag
fig, ax = plt.subplots(figsize=(10, 5))
for driver in DRIVERS:
    ax.plot(lag_table.index, lag_table[driver], marker="o", label=driver)
ax.axhline(0, color="grey", linewidth=0.8)
ax.set_title("Correlation between food inflation and each driver, by lag (Canada, 2018-2026)")
ax.set_xlabel("Lag (months the driver is shifted back)")
ax.set_ylabel("Correlation (r)")
ax.legend()
fig.tight_layout()
fig.savefig(EDA / "05_lag_correlations.png", dpi=150)
plt.show()

# ===== Part 6: seasonality of grocery prices (Canada, 2017-2026) =====
food_canada = both["food_cpi"]
monthly_change = food_canada.pct_change() * 100
by_month = monthly_change.groupby(monthly_change.index.str[5:7]).mean()
print(by_month.round(2))

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(by_month.index, by_month.values)
ax.axhline(monthly_change.mean(), color="grey", linestyle="--", label="Average of all months")
ax.set_title("Average month-to-month change in grocery prices, by calendar month (Canada, 2017-2026)")
ax.set_xlabel("Calendar month (01 = January)")
ax.set_ylabel("Average % change from previous month")
ax.legend()
fig.tight_layout()
fig.savefig(EDA / "06_seasonality_food.png", dpi=150)
plt.show()