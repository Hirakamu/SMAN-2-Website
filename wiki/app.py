
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import markdown
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')
os.makedirs(PAGES_DIR, exist_ok=True)
DB_PATH = os.path.join(os.path.dirname(__file__), 'wiki.db')

# Database setup
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
init_db()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute('SELECT password FROM users WHERE username=?', (username,))
            row = cur.fetchone()
            if row and check_password_hash(row[0], password):
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))

@app.route('/home')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    pages = [f[:-3] for f in os.listdir(PAGES_DIR) if f.endswith('.md')]
    return render_template('index.html', pages=pages, username=session['username'])

@app.route('/wiki/<page>')
def view_page(page):
    if 'username' not in session:
        return redirect(url_for('login'))
    path = os.path.join(PAGES_DIR, f'{page}.md')
    if not os.path.exists(path):
        return redirect(url_for('edit_page', page=page))
    with open(path, 'r') as f:
        content = f.read()
    html = markdown.markdown(content)
    return render_template('view.html', page=page, content=html, username=session['username'])

@app.route('/wiki/<page>/edit', methods=['GET', 'POST'])
def edit_page(page):
    if 'username' not in session:
        return redirect(url_for('login'))
    path = os.path.join(PAGES_DIR, f'{page}.md')
    if request.method == 'POST':
        with open(path, 'w') as f:
            f.write(request.form['content'])
        return redirect(url_for('view_page', page=page))
    content = ''
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
    return render_template('edit.html', page=page, content=content, username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
