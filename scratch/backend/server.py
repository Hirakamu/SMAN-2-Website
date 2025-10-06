from flask import Flask, request, abort, render_template_string
import os, sqlite3, re, markdown, secrets, json
from urllib.parse import quote_plus
from argon2 import PasswordHasher
from flask_cors import CORS
from pathlib import Path

# Configuration
passhash = PasswordHasher()
PAGEF = "article/"
AUTHDB = "auth.db"

# Init
app = Flask(__name__)
CORS(app)
articles_list = []

def indexInit():
    # Load the index JSON once at startup
    INDEX_FILE = "pageindex.json"  # or 'index.json'
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(f"{INDEX_FILE} not found")

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)

    # Flatten the nested JSON to a list of articles for easier querying
    for year, months in index.items():
        for month, days in months.items():
            for day, articles in days.items():
                for article_id, article in articles.items():
                    articles_list.append(article)

    # Sort by date descending (latest first)
    articles_list.sort(key=lambda x: x["date"], reverse=True)
    
def unSpace(text):
    text = text.strip().lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text

@app.route("/rand/")
def posts():
    latest_posts = articles_list[:9]

    data = []
    for post in latest_posts:
        data.append({
            "title": post["title"],
            "content": post.get("snippet", ""),
            "img": post.get("img", None)
        })

    return json.dumps(data, ensure_ascii=False)

@app.route("/baca")
def readarticle():
    title = request.args.get("title")
    if not title:
        abort(400, "Missing 'title' parameter")

    # Search for article by title
    article = next((a for a in articles_list if a["title"] == title), None)
    if not article:
        abort(404, "Article not found")

    # Read full JSON content
    try:
        with open(article["path"], "r", encoding="utf-8") as f:
            content_json = json.load(f)
            content_md = content_json.get("content", "")
    except Exception as e:
        abort(500, f"Failed to read article: {e}")

    # Strip first heading if it matches the title
    content_md = re.sub(rf"^#\s*{re.escape(article['title'])}\s*\n?", "", content_md, count=1)

    # Return as JSON (no HTML rendering)
    data = {
        "title": article["title"],
        "date": article["date"],
        "content": content_md,
        "img": article.get("img", None)
    }
    return json.dumps(data, ensure_ascii=False)

#--------------------- Main ---------------------#
if __name__ == "__main__":
    indexInit()
    app.run(host='0.0.0.0', port=5000, debug=True)
