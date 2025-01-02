from flask import Blueprint

blogs_bp = Blueprint('blogs', __name__)

def create_blog_routes(app, db):
    from .routes import blog_routes
    blog_routes(blogs_bp, db)
    app.register_blueprint(blogs_bp, url_prefix='/blogs')
