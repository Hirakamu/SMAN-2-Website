# backend.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"  # or "https://username.github.io"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# init db
def init_db():
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            author_id INTEGER,
            FOREIGN KEY(author_id) REFERENCES users(id)
        )""")
    conn.close()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                      (data["username"], data["password"]))
            conn.commit()
            return jsonify({"status":"ok"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"status":"fail","reason":"username taken"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (data["username"], data["password"]))
        user = c.fetchone()
    return jsonify({"status":"ok"}) if user else ({"status":"fail"}, 401)

@app.route("/article", methods=["POST"])
def post_article():
    data = request.json
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO articles (title,content,author_id) VALUES (?,?,?)",
                  (data["title"], data["content"], data["author_id"]))
        conn.commit()
    return jsonify({"status":"ok"}), 201

@app.route("/articles", methods=["GET"])
def get_articles():
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id,title,content,author_id FROM articles")
        rows = c.fetchall()
    return jsonify([{"id":r[0],"title":r[1],"content":r[2],"author":r[3]} for r in rows])

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "alive"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
