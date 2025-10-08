from flask import Flask, request, abort, send_from_directory, jsonify
import os, re, sqlite3, random
from flask_cors import CORS
from pathlib import Path
import yaml  # pip install pyyaml

# Config
ROOTS = {"article": "artikel"}
SNIPPET_LENGTH = 200
DB_FILE = "articles.db"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

app = Flask(__name__)
CORS(app)

# Utils
def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception:
        return []
    
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def fetchDB(query, params=(), fetchall=True):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(query, params)
        results = c.fetchall() if fetchall else c.fetchone()
    except sqlite3.OperationalError as e:
        print("OperationalError, rebuilding DB:", e)
        buildDB()
        conn = get_db()
        c = conn.cursor()
        c.execute(query, params)
        results = c.fetchall() if fetchall else c.fetchone()
    finally:
        conn.close()
    return results

def read_md(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                meta_yaml = parts[1]
                content_md = parts[2].strip()
                meta = yaml.safe_load(meta_yaml)
                return meta, content_md
        return {}, text
    except Exception as e:
        print("read_md error", path, e)
        return {}, ""

def buildDB():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT,
        date TEXT,
        path TEXT,
        snippet TEXT,
        img TEXT
    )
    """)
    for type_, root in ROOTS.items():
        if not os.path.isdir(root):
            continue
        for year in safe_listdir(root):
            year_path = os.path.join(root, year)
            if not os.path.isdir(year_path):
                continue
            for month in safe_listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                for day in safe_listdir(month_path):
                    day_path = os.path.join(year_path, month, day)
                    if not os.path.isdir(day_path):
                        continue
                    for file in safe_listdir(day_path):
                        filepath = os.path.join(day_path, file)
                        file_id = os.path.splitext(file)[0]
                        meta, content_md = read_md(filepath)
                        title_found = meta.get("title") or file_id
                        file_id = meta.get("uuid")
                        date = meta.get("date", f"{year}-{month}-{day}")
                        snippet = content_md[:SNIPPET_LENGTH]
                        img = meta.get("img")

                        c.execute("""
                        INSERT OR REPLACE INTO articles (id, title, date, path, snippet, img)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (file_id, title_found, date, filepath, snippet, img))
    conn.commit()
    conn.close()
    print("Database indexing completed (JSON + MD).")

# Flask
@app.route("/rand/")
def randPosts():
    all_articles = fetchDB("SELECT title, snippet, img FROM articles")
    if not all_articles:
        abort(500, "No articles indexed")

    sample = random.sample(all_articles, min(8, len(all_articles)))
    data = [{"title": r["title"], "content": r["snippet"], "img": r["img"]} for r in sample]
    return jsonify(data)

@app.route("/baca")
def readArticle():
    title = request.args.get("title")
    if not title:
        abort(400, "Missing 'title' parameter")
    article = fetchDB("SELECT * FROM articles WHERE title=?", (title,), fetchall=False)
    if not article: abort(404, "Article not found")
    _, content_md = read_md(article["path"])
    content_md = re.sub(rf"^#\s*{re.escape(article['title'])}\s*\n?", "", content_md, count=1)

    data = {
        "title": article["title"],
        "date": article["date"],
        "content": content_md,
        "img": article["img"]
    }
    return jsonify(data)

@app.route("/reindex", methods=["POST"])
def reIndex():
    buildDB()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM articles")
    count = c.fetchone()[0]
    conn.close()
    return jsonify({"status": "ok", "count": count})

# Run
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
