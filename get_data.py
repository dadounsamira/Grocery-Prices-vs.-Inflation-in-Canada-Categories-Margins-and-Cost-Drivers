# Download public data for CIND820 capstone project.

from datetime import date
from pathlib import Path

import requests

# Today s date added to the file names so we know when data was downloaded
TODAY=date.today().isoformat()

# Create folder where the raw download are saved
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# Dataset1 : Monthly average retail price ( table 18-10-0245-01)
table_id = "18100245"
api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{table_id}/en"

response = requests.get(api_url, timeout=60)
print(response.status_code)
print(response.json())





