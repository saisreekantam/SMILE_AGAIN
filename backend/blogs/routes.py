# blogs/routes.py
import logging
from typing import Tuple, Dict, Any, Union
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Blog
from extensions import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize blueprint
blogs_bp = Blueprint('blogs', __name__)

@blogs_bp.route('/blogs', methods=['POST', 'GET', 'OPTIONS'])
def blog_operations() -> Tuple[Dict[str, Any], int]:
    """
    Handle blog operations with proper method routing
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response and status code
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    if request.method == 'GET':
        return get_blogs()
        
    if request.method == 'POST':
        return create_blog()
        
    return jsonify({'error': 'Method not allowed'}), 405

@login_required
def create_blog() -> Tuple[Dict[str, Any], int]:
    """
    Create a new blog post
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response and status code
    """
    try:
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        # Create new blog
        blog = Blog(
            title=title,
            content=content,
            user_id=current_user.id
        )
        
        db.session.add(blog)
        db.session.commit()
        
        logger.info(f"Blog created successfully by user {current_user.id}")
        
        return jsonify({
            'message': 'Blog created successfully',
            'blog_id': blog.id,
            'title': blog.title
        }), 200

    except Exception as e:
        logger.error(f"Error creating blog: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create blog'}), 500

def get_blogs() -> Tuple[Dict[str, Any], int]:
    """
    Retrieve all blog posts
    
    Returns:
        Tuple[Dict[str, Any], int]: JSON response and status code
    """
    try:
        blogs = Blog.query.order_by(Blog.created_at.desc()).all()
        blogs_list = [blog.to_dict() for blog in blogs]
        
        return jsonify(blogs_list), 200

    except Exception as e:
        logger.error(f"Error retrieving blogs: {str(e)}")
        return jsonify({'error': 'Failed to retrieve blogs'}), 500