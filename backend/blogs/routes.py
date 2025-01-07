import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Blog, Comment, User
from extensions import db
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize blueprint
blogs_bp = Blueprint('blogs', __name__)

@blogs_bp.route('/blogs', methods=['GET', 'POST'])
@login_required
def blog_operations() -> Tuple[Dict[str, Any], int]:
    """Handle blog listing and creation operations."""
    if request.method == 'GET':
        try:
            # Get all blogs ordered by creation date
            blogs = Blog.query.order_by(Blog.created_at.desc()).all()
            blogs_list = []
            for blog in blogs:
                blog_dict = blog.to_dict()
                # Add author name to each blog
                author = User.query.get(blog.user_id)
                blog_dict['author_name'] = author.name if author else 'Unknown'
                blogs_list.append(blog_dict)
            return jsonify(blogs_list), 200
        except Exception as e:
            logger.error(f"Error retrieving blogs: {str(e)}")
            return jsonify({'error': 'Failed to retrieve blogs'}), 500

    # POST request - Create new blog
    try:
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400

        # Create new blog post
        new_blog = Blog(
            title=data['title'],
            content=data['content'],
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_blog)
        db.session.commit()
        
        return jsonify({
            'message': 'Blog created successfully',
            'blog_id': new_blog.id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating blog: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create blog'}), 500

@blogs_bp.route('/blogs/<int:blog_id>/comments', methods=['GET', 'POST'])
@login_required
def handle_comments(blog_id: int) -> Tuple[Dict[str, Any], int]:
    """Handle blog comment operations."""
    # Verify blog exists
    blog = Blog.query.get_or_404(blog_id)
    
    if request.method == 'GET':
        try:
            # Get all comments for the blog
            comments = Comment.query.filter_by(blog_id=blog_id)\
                .order_by(Comment.created_at.desc()).all()
            comments_list = []
            for comment in comments:
                comment_dict = comment.to_dict()
                # Add author name to each comment
                author = User.query.get(comment.user_id)
                comment_dict['author_name'] = author.name if author else 'Unknown'
                comments_list.append(comment_dict)
            return jsonify(comments_list), 200
        except Exception as e:
            logger.error(f"Error retrieving comments: {str(e)}")
            return jsonify({'error': 'Failed to retrieve comments'}), 500
            
    # POST request - Add new comment
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Comment content is required'}), 400
            
        new_comment = Comment(
            content=data['content'],
            blog_id=blog_id,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': new_comment.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add comment'}), 500

@blogs_bp.errorhandler(404)
def not_found_error(error: Exception) -> Tuple[Dict[str, str], int]:
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404

@blogs_bp.errorhandler(500)
def internal_error(error: Exception) -> Tuple[Dict[str, str], int]:
    """Handle 500 errors."""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500