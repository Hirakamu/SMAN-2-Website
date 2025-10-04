# backend.py
from flask import Flask, request, jsonify, make_response
import sqlite3
import secrets
import os

# configuration
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500")  # set to your frontend origin
API_HOST = "0.0.0.0"
API_PORT = 5000

# allowed origins - include any dev/prod origins you will use
ALLOWED_ORIGINS = {
    FRONTEND_ORIGIN,
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:5000",
    "https://username.github.io",
}

# cookie flags
USE_SECURE_COOKIE = FRONTEND_ORIGIN.startswith("https://")
COOKIE_SAMESITE = "None" if USE_SECURE_COOKIE else "Lax"
COOKIE_SECURE = True if USE_SECURE_COOKIE else False

app = Flask(__name__)

# --- DB init ---
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
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )""")
        conn.commit()

# --- session helpers ---
def create_session(user_id):
    token = secrets.token_urlsafe(32)
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        conn.commit()
    return token

def get_user_by_token(token):
    if not token:
        return None
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute(
            "SELECT users.id, users.username FROM sessions JOIN users ON sessions.user_id = users.id WHERE sessions.token = ?",
            (token,)
        )
        row = c.fetchone()
    return {"id": row[0], "username": row[1]} if row else None

def delete_session(token):
    if not token:
        return
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()

# --- CORS handler ---
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# generic OPTIONS preflight responder
@app.route("/<path:_any>", methods=["OPTIONS"])
@app.route("/", methods=["OPTIONS"])
def preflight(_any=None):
    resp = make_response()
    origin = request.headers.get("Origin")
    if origin and origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp

# --- routes ---
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "fail", "reason": "missing fields"}), 400

    try:
        with sqlite3.connect("site.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, password))
            conn.commit()
            user_id = c.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"status":"fail","reason":"username taken"}), 400

    token = create_session(user_id)
    resp = make_response(jsonify({"status":"ok"}), 201)
    resp.set_cookie("session", token, httponly=True, samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)
    return resp

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status":"fail", "reason":"missing fields"}), 400

    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        row = c.fetchone()

    if row:
        user_id = row[0]
        token = create_session(user_id)
        resp = make_response(jsonify({"status":"ok"}))
        resp.set_cookie("session", token, httponly=True, samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)
        return resp

    return jsonify({"status":"fail"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("session")
    if token:
        delete_session(token)
    resp = make_response(jsonify({"status":"ok"}))
    resp.set_cookie("session", "", expires=0)
    return resp

@app.route("/me", methods=["GET"])
def me():
    token = request.cookies.get("session")
    user = get_user_by_token(token)
    if user:
        return jsonify({"id": user["id"], "username": user["username"]})
    return jsonify({"status":"anonymous"}), 401

@app.route("/article", methods=["POST"])
def post_article():
    data = request.json or {}
    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")
    if not title or not content or not author_id:
        return jsonify({"status":"fail", "reason":"missing fields"}), 400

    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO articles (title,content,author_id) VALUES (?,?,?)", (title, content, author_id))
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

# --- start ---
if __name__ == "__main__":
    init_db()
    app.run(host=API_HOST, port=API_PORT)
