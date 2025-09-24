
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import markdown
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

print(__file__)

DATALOC = '/var/www/sman2wiki/data/'
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
PAGES_DIR = os.path.join(DATALOC, 'wikipages')
os.makedirs(PAGES_DIR, exist_ok=True)

# Database setup
DB_PATH = os.path.join(DATALOC, 'users.db')
CONFIG_PATH = os.path.join(DATALOC, 'init.flag')


# Profile management
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('login'))
    user = get_user(session['user'])
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        errors = []
        # Username change
        if new_username and new_username != user['username']:
            if get_user(new_username):
                errors.append('Username already exists.')
            else:
                # Change username in DB
                conn = get_db()
                c = conn.cursor()
                c.execute('UPDATE users SET username=? WHERE username=?', (new_username, user['username']))
                conn.commit()
                conn.close()
                session['user'] = new_username
                flash('Username updated.')
        # Password change
        if new_password:
            if not check_password_hash(user['password'], current_password):
                errors.append('Current password is incorrect.')
            elif new_password != confirm_password:
                errors.append('New passwords do not match.')
            else:
                conn = get_db()
                c = conn.cursor()
                c.execute('UPDATE users SET password=? WHERE username=?', (generate_password_hash(new_password), session['user']))
                conn.commit()
                conn.close()
                flash('Password updated.')
        for error in errors:
            flash(error)
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)
# Enhanced Wiki: News Portal Style

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialization logic
def init_app():
    if not os.path.exists(CONFIG_PATH):
        conn = get_db()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')
        # Create default admin user
        admin_user = 'admin'
        admin_pass = 'admin2025'
        c.execute('SELECT * FROM users WHERE username=?', (admin_user,))
        if not c.fetchone():
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      (admin_user, generate_password_hash(admin_pass), 'admin'))
        conn.commit()
        conn.close()
        # Write flag file
        with open(CONFIG_PATH, 'w') as f:
            f.write('initialized=true\n')
        print('Initialization complete. Default admin: admin/admin2025')
    else:
        print('App already initialized.')

init_app()



# Helper: get page metadata

TRASH_DIR = os.path.join(DATALOC, 'trash')
os.makedirs(TRASH_DIR, exist_ok=True)
DELETED_DIR = os.path.join(DATALOC, 'deleted')
os.makedirs(DELETED_DIR, exist_ok=True)

def get_pages():
    pages = []
    for fname in os.listdir(PAGES_DIR):
        if fname.endswith('.md'):
            path = os.path.join(PAGES_DIR, fname)
            stat = os.stat(path)
            author = 'Anonymous'
            # Try to read author from file header
            with open(path, 'r') as f:
                first_line = f.readline()
                if first_line.startswith('Author: '):
                    author = first_line[len('Author: '):].strip()
            pages.append({
                'title': fname[:-3],
                'date': datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y'),
                'author': author,
                'filename': fname
            })
    # Sort by last modified
    return sorted(pages, key=lambda x: x['date'], reverse=True)

def get_trashed_pages():
    pages = []
    for fname in os.listdir(TRASH_DIR):
        if fname.endswith('.md'):
            path = os.path.join(TRASH_DIR, fname)
            stat = os.stat(path)
            author = 'Anonymous'
            with open(path, 'r') as f:
                first_line = f.readline()
                if first_line.startswith('Author: '):
                    author = first_line[len('Author: '):].strip()
            pages.append({
                'title': fname[:-3],
                'date': datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y'),
                'author': author,
                'filename': fname
            })
    return sorted(pages, key=lambda x: x['date'], reverse=True)

# User authentication helpers
def get_user(username):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def is_logged_in():
    return 'user' in session

def is_admin():
    return session.get('role') == 'admin'


@app.route('/')
def landing():
    latest = get_pages()[:5]
    categories = ['Berita', 'Artikel', 'Prestasi', 'Pendidikan']
    return render_template('landing.html', is_admin=is_admin(), latest=latest, categories=categories)




@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_logged_in() or not is_admin():
        return redirect(url_for('login'))
    lockfile = os.path.join(PAGES_DIR, '.locked_pages')
    locked_pages = set()
    if os.path.exists(lockfile):
        with open(lockfile, 'r') as f:
            locked_pages = set(line.strip() for line in f if line.strip())
    if request.method == 'POST':
        # Lock/unlock
        page = request.form.get('page')
        if page and 'lock' in request.form:
            if page in locked_pages:
                locked_pages.remove(page)
            else:
                locked_pages.add(page)
            with open(lockfile, 'w') as f:
                for p in locked_pages:
                    f.write(p + '\n')
            flash(f'Lock status updated for {page}')
        # Restore
        restore_page = request.form.get('restore')
        if restore_page:
            src = os.path.join(TRASH_DIR, f'{restore_page}.md')
            dst = os.path.join(PAGES_DIR, f'{restore_page}.md')
            if os.path.exists(src):
                os.rename(src, dst)
                flash(f'Restored page: {restore_page}')
        # Delete permanently
        delete_page = request.form.get('delete_permanent')
        if delete_page:
            src = os.path.join(TRASH_DIR, f'{delete_page}.md')
            dst = os.path.join(DELETED_DIR, f'{delete_page}.md')
            if os.path.exists(src):
                os.rename(src, dst)
                flash(f'Permanently deleted page: {delete_page}')
        return redirect(url_for('admin'))
    pages = get_pages()
    trashed = get_trashed_pages()
    return render_template('admin.html', pages=pages, locked_pages=locked_pages, trashed=trashed)


# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password required.')
            return redirect(url_for('register'))
        if get_user(username):
            flash('Username already exists.')
            return redirect(url_for('register'))
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, generate_password_hash(password), 'user'))
        conn.commit()
        conn.close()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            flash('Logged in successfully.')
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

# User logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('Logged out.')
    return redirect(url_for('landing'))


# Remove old admin login/logout routes


@app.route('/artikel')
def index():
    pages = get_pages()
    categories = ['Berita', 'Artikel', 'Prestasi', 'Pendidikan']
    return render_template('index.html', pages=pages, categories=categories, logged_in=is_logged_in())

@app.route('/artikel/<page>')
def view_page(page):
    path = os.path.join(PAGES_DIR, f'{page}.md')
    if not os.path.exists(path):
        return redirect(url_for('edit_page', page=page))
    with open(path, 'r') as f:
        lines = f.readlines()
        author = 'Anonymous'
        if lines and lines[0].startswith('Author: '):
            author = lines[0][len('Author: '):].strip()
            content = ''.join(lines[1:])
        else:
            content = ''.join(lines)
    html = markdown.markdown(content)
    stat = os.stat(path)
    meta = {
        'title': page,
        'date': datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y'),
        'author': author
    }
    return render_template('view.html', page=page, content=html, meta=meta)



@app.route('/artikel/<page>/edit', methods=['GET', 'POST'])
def edit_page(page):
    path = os.path.join(PAGES_DIR, f'{page}.md')
    lockfile = os.path.join(PAGES_DIR, '.locked_pages')
    locked_pages = set()
    if os.path.exists(lockfile):
        with open(lockfile, 'r') as f:
            locked_pages = set(line.strip() for line in f if line.strip())
    if page in locked_pages and not session.get('is_admin'):
        flash('This page is locked by admin. Only admin can edit.')
        return redirect(url_for('view_page', page=page))
    author = 'Anonymous'
    content = ''
    if os.path.exists(path):
        with open(path, 'r') as f:
            lines = f.readlines()
            if lines and lines[0].startswith('Author: '):
                author = lines[0][len('Author: '):].strip()
                content = ''.join(lines[1:])
            else:
                content = ''.join(lines)
    if request.method == 'POST':
        # Delete page
        if 'delete' in request.form:
            trash_path = os.path.join(TRASH_DIR, f'{page}.md')
            if os.path.exists(path):
                os.rename(path, trash_path)
                flash(f'Page {page} moved to trash.')
            return redirect(url_for('index'))
        new_title = request.form.get('title', page).strip()
        content = request.form['content']
        new_path = os.path.join(PAGES_DIR, f'{new_title}.md')
        # If title changed and file exists, rename
        if new_title != page:
            if os.path.exists(new_path):
                flash('A page with that title already exists.')
                return redirect(url_for('edit_page', page=page))
            if os.path.exists(path):
                os.rename(path, new_path)
            path = new_path
            page = new_title
        # Write content to new or existing file, with author header
        author = session.get('user', 'Anonymous')
        with open(path, 'w') as f:
            f.write(f'Author: {author}\n') 
            f.write(content)
        return redirect(url_for('view_page', page=page))
    meta = {'title': page, 'author': author}
    return render_template('edit.html', page=page, content=content, meta=meta)

if __name__ == '__main__':
    app.run(debug=True)
