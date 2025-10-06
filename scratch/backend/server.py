from flask import Flask, request, abort, send_from_directory, jsonify
import os, re, json, random
from flask_cors import CORS

# Config
ROOTS = {"article": "artikel"}
SNIPPET_LENGTH = 200

app = Flask(__name__)
CORS(app)

articles_list = []

def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception:
        return []

def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("read_json error", path, e)
        return {}

def build_index():
    index = {}
    for type_, root in ROOTS.items():
        if not os.path.isdir(root):
            continue
        for year in safe_listdir(root):
            year_path = os.path.join(root, year)
            if not os.path.isdir(year_path):
                continue
            index.setdefault(year, {})
            for month in safe_listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                index[year].setdefault(month, {})
                for day in safe_listdir(month_path):
                    day_path = os.path.join(month_path, day)
                    if not os.path.isdir(day_path):
                        continue
                    index[year][month].setdefault(day, {})
                    for file in safe_listdir(day_path):
                        if not file.lower().endswith(".json"):
                            continue
                        filepath = os.path.join(day_path, file)
                        file_id = os.path.splitext(file)[0]
                        content_json = read_json(filepath)
                        content_text = content_json.get("content", "") or ""
                        # find first heading as title if present
                        title_found = None
                        snippet_parts = []
                        for line in content_text.splitlines():
                            s = line.strip()
                            if not s:
                                continue
                            if s.startswith("#") and title_found is None:
                                title_found = s.lstrip("#").strip()
                                continue
                            snippet_parts.append(s)
                        snippet = " ".join(snippet_parts)
                        snippet = snippet[:SNIPPET_LENGTH] + ("..." if len(snippet) > SNIPPET_LENGTH else "")
                        index[year][month][day][file_id] = {
                            "title": title_found if title_found else file_id,
                            "date": f"{year}-{month}-{day}",
                            "path": filepath,
                            "snippet": snippet,
                            "img": content_json.get("img")
                        }
    return index

def indexInit():
    global articles_list
    index = build_index()
    articles_list = []
    for year, months in index.items():
        for month, days in months.items():
            for day, articles in days.items():
                for article_id, article in articles.items():
                    articles_list.append(article)
    # sort by date (string ISO style) desc
    articles_list.sort(key=lambda x: x.get("date", ""), reverse=True)
    print(f"Indexed {len(articles_list)} articles.")

def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text

# serve assets from local 'assets' folder next to this file
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../frontend/assets")

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    if not os.path.isdir(ASSETS_DIR):
        abort(404, "assets folder not found on server")
    return send_from_directory(ASSETS_DIR, filename)

@app.route("/rand/")
def randPosts():
    if not articles_list:
        abort(500, "No articles indexed")
    defaultPosts = 9
    sample = random.sample(articles_list, min(defaultPosts, len(articles_list)))
    data = [
        {
            "title": p.get("title"),
            "content": p.get("snippet", ""),
            "img": p.get("img")
        } for p in sample
    ]
    return jsonify(data)

@app.route("/baca")
def readArticle():
    title = request.args.get("title")
    if not title:
        abort(400, "Missing 'title' parameter")
    # exact-match search on title (case-sensitive as stored). consider normalizing if needed.
    article = next((a for a in articles_list if a.get("title") == title), None)
    if not article:
        abort(404, "Article not found")
    content_json = read_json(article["path"])
    content_md = content_json.get("content", "")
    # strip first heading if it matches title
    content_md = re.sub(rf"^#\s*{re.escape(article['title'])}\s*\n?", "", content_md, count=1)
    data = {
        "title": article["title"],
        "date": article["date"],
        "content": content_md,
        "img": article.get("img")
    }
    return jsonify(data)

@app.route("/reindex", methods=["POST"])
def reIndex():
    indexInit()
    return jsonify({"status": "ok", "count": len(articles_list)})

if __name__ == "__main__":
    indexInit()
    app.run(host='0.0.0.0', port=5000, debug=True)
