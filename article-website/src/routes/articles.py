from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from src.models import Article
from src.database import sman_db as db_session

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/articles', methods=['GET'])
@login_required
def list_articles():
    articles = Article.query.filter_by(user_id=current_user.id).all()
    return render_template('articles.html', articles=articles)

@articles_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_article = Article(title=title, content=content, user_id=current_user.id)
        db_session.add(new_article)
        db_session.commit()
        flash('Article created successfully!', 'success')
        return redirect(url_for('articles.list_articles'))
    return render_template('new_article.html')

@articles_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('You do not have permission to edit this article.', 'danger')
        return redirect(url_for('articles.list_articles'))
    
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        db_session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('articles.list_articles'))
    
    return render_template('edit_article.html', article=article)

@articles_bp.route('/articles/trash/<int:article_id>', methods=['POST'])
@login_required
def move_to_trash(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id == current_user.id:
        article.is_trashed = True
        db_session.commit()
        flash('Article moved to trash.', 'success')
    return redirect(url_for('articles.list_articles'))

@articles_bp.route('/articles/delete/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id == current_user.id:
        db_session.delete(article)
        db_session.commit()
        flash('Article deleted permanently.', 'success')
    return redirect(url_for('articles.list_articles'))