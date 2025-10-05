from flask import Flask, request, jsonify, make_response
import os, sqlite3, re, markdown2, secrets, time
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

#--------------------- DEFs ---------------------#
def dbAuthInit():
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Sessions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
def unSpace(text):
    text = text.strip().lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text
def sessionCreate(user_id):
    token = secrets.token_urlsafe(32)
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token
def getUsername(username):
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row
def getEmail(email):
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row
def getToken(token):
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    c.execute("SELECT user_id FROM sessions WHERE token=?", (token,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None



#--------------------- Routes -------------------#
@app.route("/request_register/", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return jsonify({"error": "Missing fields"}), 400
    
    if getUsername(username):
        return jsonify({"error": "Username already exists"}), 400
    if getEmail(email):
        return jsonify({"error": "Email already exists"}), 400
    
    password_hash = passhash.hash(password)
    conn = sqlite3.connect(AUTHDB)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
              (username, email, password_hash))
    user_id = c.lastrowid
    conn.commit()
    conn.close()

    token = sessionCreate(user_id)
    resp = make_response(jsonify({"message": "Registered successfully"}))
    resp.set_cookie("session_token", token, httponly=True, samesite='Strict')
    return resp
@app.route("/request_login/", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400
    
    user = getUsername(username)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    user_id, user_name, password_hash = user
    try:
        passhash.verify(password_hash, password)
    except:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = sessionCreate(user_id)
    resp = make_response(jsonify({"message": "Logged in successfully"}))
    resp.set_cookie("session_token", token, httponly=True, samesite='Strict')
    return resp
@app.route("/me/", methods=["GET"])
def me():
    token = request.cookies.get("session_token")
    if not token:
        return jsonify({"error": "Not authenticated"}), 401
    user_id = getToken(token)
    if not user_id:
        return jsonify({"error": "Invalid session"}), 401
    return jsonify({"user_id": user_id})
@app.route("/logout/", methods=["POST"])
def logout():
    token = request.cookies.get("session_token")
    if token:
        conn = sqlite3.connect(AUTHDB)
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
        conn.close()
    resp = make_response(jsonify({"message": "Logged out"}))
    resp.delete_cookie("session_token")
    return resp
@app.route("/post/")
def posts():
    return "Backend in maintenance mode", 503
@app.route("/post/baca")
def readarticle():
    return "Backend in maintenance mode", 503

#--------------------- Main ---------------------#
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
