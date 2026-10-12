import zipfile
from pathlib import Path

import pandas as pd

#Folder where get_data.py saved the raw downloads

RAW = Path ("data/raw")

def read_latest_statcan(table_id):
    """ Read the most recent saved zip of Statistics Canada table into a DataFrame."""
    zip_path = sorted(RAW.glob(f"statcan_{table_id}_*.zip"))[-1]
    print("Reading:", zip_path)
    with zipfile.ZipFile(zip_path) as z:
        with z.open(f"{table_id}.csv") as f:
            return pd.read_csv(f,low_memory=False)


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