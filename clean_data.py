import zipfile
from pathlib import Path
import pandas as pd
import json

#Folder where get_data.py saved the raw downloads

RAW = Path ("data/raw")

def read_latest_statcan(table_id):
    """ Read the most recent saved zip of Statistics Canada table into a DataFrame."""
    zip_path = sorted(RAW.glob(f"statcan_{table_id}_*.zip"))[-1]
    print("Reading:", zip_path)
    with zipfile.ZipFile(zip_path) as z:
        with z.open(f"{table_id}.csv") as f:
            return pd.read_csv(f,low_memory=False)

def read_latest_boc(name):
    """Read the most recent saved Bank of Canada JSON file into a dictionary."""
    json_path = sorted(RAW.glob(f"boc_{name}_*.json"))[-1]
    print("Reading:", json_path)
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)



#Retail prices : list every product so we can seperate food from non-food
prices = read_latest_statcan("18100245")
products = sorted(prices["Products"].unique())
print("Number of products:", len(products))
#for product in products:
#    print(product)


# AUDIT: which product names have hidden spaces at the start or end?
for product in products:
    if product != product.strip():
        print("Hidden space:", repr(product))

# CLEAN: remove those spaces
prices["Products"] = prices["Products"].str.strip()

# Non-food items in the retail price table (decision #18)
NON_FOOD = [
    "Deodorant, 85 grams",
    "Laundry detergent, 4.43 litres",
    "Shampoo, 400 millilitres",
    "Toothpaste, 100 millilitres",
]

# Keep only food products
food_prices = prices[~prices["Products"].isin(NON_FOOD)]

print("Rows before:", len(prices), "| after removing non-food:", len(food_prices))
print("Food products:", food_prices["Products"].nunique())

# AUDIT: missing prices and quality flags in the food table
print("Missing prices:", food_prices["VALUE"].isna().sum())
print("Quality flags (STATUS):")
print(food_prices["STATUS"].value_counts(dropna=False))

# AUDIT: where are the missing prices?
missing = food_prices[food_prices["VALUE"].isna()]
print(missing.groupby(["Products", "GEO"]).size())

# AUDIT: does every product cover the whole period? (absent rows, not empty cells)
print("Months in the table:", food_prices["REF_DATE"].nunique())
canada = food_prices[food_prices["GEO"] == "Canada"]
months_per_product = canada.groupby("Products")["REF_DATE"].nunique()
print(months_per_product.sort_values().head(20))

# AUDIT: how many food products does each geography have?
products_per_geo = food_prices.groupby("GEO")["Products"].nunique()
print(products_per_geo.sort_values())

# AUDIT: rows missing within existing product series, per geography
rows_per_geo = food_prices.groupby("GEO").size()
expected_rows = products_per_geo * 115
print((expected_rows - rows_per_geo).sort_values())

# AUDIT: what period do the territories actually cover?
TERRITORIES = ["Whitehorse, Yukon", "Yellowknife, Northwest Territories"]
territories = food_prices[food_prices["GEO"].isin(TERRITORIES)]
print(territories.groupby("GEO")["REF_DATE"].agg(["min", "max", "nunique"]))

# CLEAN: keep Canada + 10 provinces (territories only have 11 months, decision #19)
retail = food_prices[~food_prices["GEO"].isin(TERRITORIES)]

# VERIFY: the cleaned table should be complete
print("Geographies kept:", retail["GEO"].nunique())
print("Rows:", len(retail), "| expected:", 106 * 11 * 115 - 115)
print("Missing prices:", retail["VALUE"].isna().sum())


# SAVE: keep only the columns we need and save the clean retail table
CLEAN = Path("data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)
retail_clean = retail[["REF_DATE", "GEO", "Products", "VALUE"]]
retail_clean.to_csv(CLEAN / "retail_prices_clean.csv", index=False)
print("Saved:", CLEAN / "retail_prices_clean.csv", retail_clean.shape)

# ===== CPI (table 18-10-0004-01) =====
cpi = read_latest_statcan("18100004")
# AUDIT: what does the table look like?
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
print(cpi.columns.tolist())
print(cpi.head())
print("CPI rows:", len(cpi))
print("Units (UOM):",cpi["UOM"].unique())
cpi_groups = sorted(cpi["Products and product groups"].unique())
print(cpi["UOM"].value_counts())
print("Number of product groups:", len(cpi_groups))
food_groups = [g for g in cpi_groups if "food" in g.lower()]
print("Groups containing 'food':")
for group in food_groups:
    print("  ", group)

# AUDIT: do the groups we want exist with these exact names?
CPI_KEEP = ["All-items",
            "Food",
            "Food purchased from stores",
            "Meat",
            "Fish, seafood and other marine products",
            "Dairy products and eggs",
            "Bakery and cereal products (excluding baby food)",
            "Fruit, fruit preparations and nuts",
            "Vegetables and vegetable preparations",
            "Other food products and non-alcoholic beverages"]
#for name in CPI_KEEP:
    #print(name in cpi_groups, "|", name)

# AUDIT: which places are in the CPI table?
cpi_geos = sorted(cpi["GEO"].unique())
print("Number of places:", len(cpi_geos))
for geo in cpi_geos:
    print("  ", geo)

# CLEAN: keep our 10 groups and Canada + 10 provinces
CPI_GEOS = ["Canada",
            "Newfoundland and Labrador", "Prince Edward Island",
            "Nova Scotia", "New Brunswick", "Quebec", "Ontario",
            "Manitoba", "Saskatchewan", "Alberta", "British Columbia"]
keep_group = cpi["Products and product groups"].isin(CPI_KEEP)
keep_geo = cpi["GEO"].isin(CPI_GEOS)
cpi_food = cpi[keep_group & keep_geo]
print("Rows before:", len(cpi), "| after:", len(cpi_food))
print("Places:", cpi_food["GEO"].nunique(),
      "| Groups:", cpi_food["Products and product groups"].nunique())

# AUDIT: dates, units and missing values in our selection
dates_per_group = cpi_food.groupby("Products and product groups")["REF_DATE"].agg(["min", "max", "nunique"])
print(dates_per_group)
print("Units:", cpi_food["UOM"].unique())
print("Missing values:", cpi_food["VALUE"].isna().sum())

# CLEAN: keep January 2017 onwards (same start as retail prices)
cpi_food = cpi_food[cpi_food["REF_DATE"] >= "2017-01"]

# VERIFY: 11 places x 10 groups x 116 months
months = cpi_food["REF_DATE"].nunique()
print("Months:", months, "| from", cpi_food["REF_DATE"].min(), "to", cpi_food["REF_DATE"].max())
print("Rows:", len(cpi_food), "| expected:", 11 * 10 * months)
series_lengths = cpi_food.groupby(["GEO", "Products and product groups"]).size()
print("Shortest series:", series_lengths.min(), "| longest:", series_lengths.max())

# VERIFY: any special flags?
print(cpi_food["STATUS"].value_counts(dropna=False))

# SAVE: keep the 4 useful columns, shorten the group column name
cpi_clean = cpi_food[["REF_DATE", "GEO", "Products and product groups", "VALUE"]]
cpi_clean = cpi_clean.rename(columns={"Products and product groups": "Group"})
cpi_clean.to_csv(CLEAN / "cpi_clean.csv", index=False)
print("Saved:", CLEAN / "cpi_clean.csv", cpi_clean.shape)

# ===== Bank of Canada (Valet API, JSON files) =====
# LOOK: which Bank of Canada files do we have?
for path in sorted(RAW.glob("boc_*.json")):
    print(path)

# LOOK: what is inside one file? (USD/CAD as the example)
fx_raw = read_latest_boc("FXUSDCAD")
print("Top-level keys:", list(fx_raw.keys()))
print("Number of observations:", len(fx_raw["observations"]))
print("First 2 observations:", fx_raw["observations"][:2])

# LOOK: the commodity price index group (7 series in one file)
bcpi_raw = read_latest_boc("BCPI_MONTHLY")
print("Top-level keys:", list(bcpi_raw.keys()))
for code, info in bcpi_raw["seriesDetail"].items():
    print(code, "|", info["label"])
print("Number of observations:", len(bcpi_raw["observations"]))
print("First observation:", bcpi_raw["observations"][0])
print("Last observation:", bcpi_raw["observations"][-1])

# CLEAN: build a table with the month and the 2 series we need
rows = []
for obs in bcpi_raw["observations"]:
    rows.append({"month": obs["d"][:7],
                 "energy_index": obs["M.ENER"]["v"],
                 "agri_index": obs["M.AGRI"]["v"]})
bcpi = pd.DataFrame(rows)
print(bcpi.head(3))
print(bcpi.dtypes)
print("Shape:", bcpi.shape)

# CLEAN: convert the text values to numbers
bcpi["energy_index"] = pd.to_numeric(bcpi["energy_index"], errors="coerce")
bcpi["agri_index"] = pd.to_numeric(bcpi["agri_index"], errors="coerce")
print(bcpi.dtypes)
print("Missing after conversion:", bcpi[["energy_index", "agri_index"]].isna().sum().sum())

# CLEAN: keep January 2017 onwards (same window as retail and CPI)
bcpi = bcpi[bcpi["month"] >= "2017-01"]

# VERIFY
print("Months:", bcpi["month"].nunique(), "| from", bcpi["month"].min(), "to", bcpi["month"].max())
print(bcpi.describe())

# ----- USD/CAD: daily values -----
rows = []
for obs in fx_raw["observations"]:
    rows.append({"month": obs["d"][:7],
                 "usdcad": obs["FXUSDCAD"]["v"]})
fx = pd.DataFrame(rows)
fx["usdcad"] = pd.to_numeric(fx["usdcad"], errors="coerce")
print("Days:", len(fx), "| missing:", fx["usdcad"].isna().sum())

# AUDIT: how many business days in each month?
days_per_month = fx.groupby("month").size()
print("Months:", days_per_month.index.min(), "to", days_per_month.index.max())
print("Days per month: min", days_per_month.min(), "| max", days_per_month.max())
print(days_per_month.sort_values().head(3))

# CLEAN: monthly average of the daily rates, complete months only (2017-01 to 2026-08)
fx_monthly = fx.groupby("month")["usdcad"].mean().reset_index()
fx_monthly = fx_monthly[fx_monthly["month"] <= "2026-08"]

# VERIFY
print("Months:", len(fx_monthly), "| from", fx_monthly["month"].min(), "to", fx_monthly["month"].max())
print(fx_monthly.head(3))
print(fx_monthly.describe())


# ----- Policy rate (V39079): daily values -----
rate_raw = read_latest_boc("V39079")
rows = []
for obs in rate_raw["observations"]:
    rows.append({"month": obs["d"][:7],
                 "policy_rate": obs["V39079"]["v"]})
rate = pd.DataFrame(rows)
rate["policy_rate"] = pd.to_numeric(rate["policy_rate"], errors="coerce")
print("Days:", len(rate), "| missing:", rate["policy_rate"].isna().sum())

# AUDIT: days per month, in our window only
in_window = (rate["month"] >= "2017-01") & (rate["month"] <= "2026-08")
days = rate[in_window].groupby("month").size()
print("Days per month: min", days.min(), "| max", days.max())

# CLEAN: monthly average, 2017-01 to 2026-08
rate_monthly = rate[in_window].groupby("month")["policy_rate"].mean().reset_index()

# VERIFY
print("Months:", len(rate_monthly), "| from", rate_monthly["month"].min(), "to", rate_monthly["month"].max())
print(rate_monthly.describe())

# ----- Combine the 3 drivers into one monthly table -----
drivers = bcpi.merge(fx_monthly, on="month").merge(rate_monthly, on="month")

# VERIFY
print("Drivers:", drivers.shape)
print("Missing:", drivers.isna().sum().sum())
print(drivers.head(3))
print(drivers.tail(3))

# SAVE
drivers.to_csv(CLEAN / "drivers_monthly.csv", index=False)
print("Saved:", CLEAN / "drivers_monthly.csv", drivers.shape)