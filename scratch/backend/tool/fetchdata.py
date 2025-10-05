import requests
import os
from datetime import datetime
import json

# API URL
url = "https://fakerapi.it/api/v1/texts?_locale=en_US&_seed=123&_quantity=100&_characters=200"

# Base directory
base_dir = "artikel"  # or "berita"

# Fetch the data
res = requests.get(url)
data = res.json()["data"]  # list of entries

# Folder path based on current date
today = datetime.today()
folder_path = os.path.join(base_dir, str(today.year), f"{today.month:02}", f"{today.day:02}")
os.makedirs(folder_path, exist_ok=True)

# Save each entry as a separate JSON file
for i, entry in enumerate(data, start=1):
    filename = f"{i}.json"  # sequential numbering
    filepath = os.path.join(folder_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

print(f"{len(data)} JSON files saved to {folder_path}")
