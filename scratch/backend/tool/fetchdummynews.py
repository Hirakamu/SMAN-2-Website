import os
import requests
import json
from datetime import datetime
import time

API_KEY = "e1d16afe9351478ea43d88f7b5e6bd11"
BASE_DIR = "news_json"
PAGE_SIZE = 100  # max allowed by NewsAPI
TOTAL_PAGES = 5  # 5 pages x 100 = 500 articles
QUERY = "technology OR science OR news"

def sanitize_filename(title):
    # Remove illegal characters for filenames
    import re
    return re.sub(r'[\\/*?:"<>|]', "", title)

counter = 1
folder_counters = {}

def save_article(article):
    date_str = article.get("publishedAt", "")
    if date_str:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    else:
        dt = datetime.utcnow()

    folder = os.path.join(BASE_DIR, str(dt.year), f"{dt.month:02}", f"{dt.day:02}")
    os.makedirs(folder, exist_ok=True)

    if folder not in folder_counters:
        folder_counters[folder] = 1

    filename = f"{folder_counters[folder]}.json"
    folder_counters[folder] += 1
    path = os.path.join(folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

def fetch_articles():
    url = "https://newsapi.org/v2/everything"
    for page in range(1, TOTAL_PAGES + 1):
        print(f"Fetching page {page}...")
        params = {
            "q": QUERY,
            "apiKey": API_KEY,
            "pageSize": PAGE_SIZE,
            "page": page,
            "language": "en",
            "sortBy": "publishedAt"
        }
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])
        for article in articles:
            save_article(article)
        time.sleep(1)  # avoid API rate limits

if __name__ == "__main__":
    fetch_articles()
    print("Done! Articles saved as JSON in 'news_json/' folder.")
