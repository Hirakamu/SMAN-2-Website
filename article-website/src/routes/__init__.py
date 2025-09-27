from flask import Blueprint, render_template

routes_bp = Blueprint('routes', __name__)

from .auth import auth_bp
from .articles import articles_bp
from .profile import profile_bp
from .admin import admin_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def home():
        return render_template('base.html')