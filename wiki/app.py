

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import markdown

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')
os.makedirs(PAGES_DIR, exist_ok=True)

# Premade admin credentials
ADMIN_USER = 'admin'
ADMIN_PASS = 's2wiki2025'

@app.route('/')
def landing():
    is_admin = session.get('is_admin', False)
    return render_template('landing.html', is_admin=is_admin)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    # Load locked pages from file
    lockfile = os.path.join(PAGES_DIR, '.locked_pages')
    locked_pages = set()
    if os.path.exists(lockfile):
        with open(lockfile, 'r') as f:
            locked_pages = set(line.strip() for line in f if line.strip())
    # Handle lock/unlock action
    if request.method == 'POST':
        page = request.form.get('page')
        if page:
            if page in locked_pages:
                locked_pages.remove(page)
            else:
                locked_pages.add(page)
            with open(lockfile, 'w') as f:
                for p in locked_pages:
                    f.write(p + '\n')
        flash(f'Lock status updated for {page}')
        return redirect(url_for('admin'))
    # List all pages
    pages = [f[:-3] for f in os.listdir(PAGES_DIR) if f.endswith('.md')]
    return render_template('admin.html', pages=pages, locked_pages=locked_pages)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['is_admin'] = True
            flash('Welcome, admin!')
            return redirect(url_for('admin'))
        else:
            flash('Invalid admin credentials.')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Logged out from admin.')
    return redirect(url_for('landing'))

@app.route('/home')
def index():
    pages = [f[:-3] for f in os.listdir(PAGES_DIR) if f.endswith('.md')]
    return render_template('index.html', pages=pages)

@app.route('/wiki/<page>')
def view_page(page):
    path = os.path.join(PAGES_DIR, f'{page}.md')
    if not os.path.exists(path):
        return redirect(url_for('edit_page', page=page))
    with open(path, 'r') as f:
        content = f.read()
    html = markdown.markdown(content)
    return render_template('view.html', page=page, content=html)

@app.route('/wiki/<page>/edit', methods=['GET', 'POST'])
def edit_page(page):
    path = os.path.join(PAGES_DIR, f'{page}.md')
    # Check if page is locked
    lockfile = os.path.join(PAGES_DIR, '.locked_pages')
    locked_pages = set()
    if os.path.exists(lockfile):
        with open(lockfile, 'r') as f:
            locked_pages = set(line.strip() for line in f if line.strip())
    if page in locked_pages and not session.get('is_admin'):
        flash('This page is locked by admin. Only admin can edit.')
        return redirect(url_for('view_page', page=page))
    if request.method == 'POST':
        with open(path, 'w') as f:
            f.write(request.form['content'])
        return redirect(url_for('view_page', page=page))
    content = ''
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
    return render_template('edit.html', page=page, content=content)

if __name__ == '__main__':
    app.run(debug=True)
