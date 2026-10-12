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