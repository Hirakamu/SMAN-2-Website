# app.py
import os, sqlite3, time, re
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import markdown2


DB_PATH = "articles.db"
ART_DIR = "article/"

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE,
    title TEXT,
    preview TEXT,
    path TEXT,
    updated_at REAL);
    """)
    conn.commit()
    conn.close()

def slugify(text):
    # convert title to URL-safe slug
    text = text.strip().lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text

def extract_title_and_preview(filepath):
    title = None
    content_preview = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            # heading as title
            if not title and line.lstrip().startswith("#"):
                title = line.strip("# ").strip()
                continue
            # skip non-text (tables, list, blockquote, code)
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("|", "-", ">", "`", "*", "+", "#")):
                continue
            # collect text
            content_preview.append(stripped)
            if len(" ".join(content_preview)) > 200:
                break
    preview = " ".join(content_preview)[:200]
    return title or os.path.basename(filepath), preview

def sync_articles():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for fname in os.listdir(ART_DIR):
        if fname.endswith(".md"):
            fpath = os.path.join(ART_DIR, fname)
            mtime = os.path.getmtime(fpath)
            title, preview = extract_title_and_preview(fpath)
            cur.execute("""
            INSERT OR IGNORE INTO articles (filename, title, preview, path, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (fname, title, preview, fpath, mtime))
            cur.execute("""
            UPDATE articles SET updated_at=?, title=?, preview=?
            WHERE filename=? AND updated_at<?
            """, (mtime, title, preview, fname, mtime))
    conn.commit()
    conn.close()

@app.route("/post/")
def get_posts():
    limit = request.args.get("posts", default=5, type=int)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT title, preview FROM articles ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/post/baca")
def get_post():
    slug = request.args.get("title")
    if not slug:
        return jsonify({"error": "Missing title parameter"}), 400

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT title, path FROM articles")
    row = None
    for r in cur.fetchall():
        if slugify(r["title"]) == slug:
            row = r
            break
    conn.close()

    if not row:
        return jsonify({"error": "Article not found"}), 404

    # Read Markdown file
    md_path = row["path"]
    if not os.path.exists(md_path):
        return jsonify({"error": "Markdown file not found"}), 404

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert Markdown to HTML
    html_content = markdown2.markdown(md_content, extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists"])

    return jsonify({
        "title": row["title"],
        "html": html_content
    })

if __name__ == "__main__":
    init_db()
    sync_articles()
    app.run(debug=True)
