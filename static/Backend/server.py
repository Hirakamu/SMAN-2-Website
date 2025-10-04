# backend.py
from flask import Flask, request, jsonify
import sqlite3
import secrets
from flask import make_response

FRONTEND_ORIGIN = "http://localhost:5500"  # set to your frontend origin (e.g. https://username.github.io)
API_HOST = "0.0.0.0"
API_PORT = 5000

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
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
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )""")
    conn.close()

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
        c.execute("SELECT users.id, users.username FROM sessions JOIN users ON sessions.user_id = users.id WHERE sessions.token = ?", (token,))
        row = c.fetchone()
    return {"id": row[0], "username": row[1]} if row else None

def delete_session(token):
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                      (data["username"], data["password"]))
            conn.commit()
            user_id = c.lastrowid
            token = create_session(user_id)
            resp = make_response(jsonify({"status":"ok"}), 201)
            resp.set_cookie("session", token, httponly=True, samesite="Lax")  # secure=True in prod with HTTPS
            return resp
        except sqlite3.IntegrityError:
            return jsonify({"status":"fail","reason":"username taken"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    with sqlite3.connect("site.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?",
                  (data["username"], data["password"]))
        row = c.fetchone()
    if row:
        user_id = row[0]
        token = create_session(user_id)
        resp = make_response(jsonify({"status":"ok"}))
        resp.set_cookie("session", token, httponly=True, samesite="Lax")
        return resp
    return jsonify({"status":"fail"}), 401

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

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
