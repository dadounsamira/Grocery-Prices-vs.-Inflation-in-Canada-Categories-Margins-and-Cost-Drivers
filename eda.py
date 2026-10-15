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
