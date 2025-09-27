from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from ..models import User, Article
from ..database import sman_db as db_session

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    articles = Article.query.filter_by(author_id=current_user.id).all()
    return render_template('profile.html', articles=articles)

@profile_bp.route('/profile/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id:
        flash('You do not have permission to edit this article.', 'danger')
        return redirect(url_for('profile.profile'))

    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        db_session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('edit_article.html', article=article)

@profile_bp.route('/profile/trash/<int:article_id>')
@login_required
def trash_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id:
        flash('You do not have permission to move this article to trash.', 'danger')
        return redirect(url_for('profile.profile'))

    article.is_trashed = True
    db_session.commit()
    flash('Article moved to trash!', 'success')
    return redirect(url_for('profile.profile'))

@profile_bp.route('/profile/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id:
        flash('You do not have permission to delete this article.', 'danger')
        return redirect(url_for('profile.profile'))

    db_session.delete(article)
    db_session.commit()
    flash('Article deleted permanently!', 'success')
    return redirect(url_for('profile.profile'))