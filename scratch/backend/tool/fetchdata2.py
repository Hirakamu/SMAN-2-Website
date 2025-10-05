import requests
import os
from datetime import datetime
import json

# API URL
url = "https://fakerapi.it/api/v1/texts?_locale=en_US&_seed=3737&_quantity=512&_characters=2048"

# Base directory
base_dir = "artikel"  # or "berita"

# Fetch the data
res = requests.get(url)
data = res.json()["data"]  # list of entries

# Folder path based on current date
today = datetime.today()
folder_path = os.path.join(base_dir, str(today.year), f"{today.month:02}", f"{today.day:02}")
os.makedirs(folder_path, exist_ok=True)

# Save each entry as JSON with Markdown-formatted content
for i, entry in enumerate(data, start=1):
    # Convert content to Markdown format
    md_content = f"# {entry['title']}\n\n{entry['content']}"
    entry["content"] = md_content

    filename = f"{i}.json"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

print(f"{len(data)} JSON files with Markdown content saved to {folder_path}")
