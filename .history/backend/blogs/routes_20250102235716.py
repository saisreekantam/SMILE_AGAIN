from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import Community, Blog, Comment, User
from app import db
from .utils import get_online_users

blogs_bp = Blueprint('main', __name__)

def register_routes(app):
    app.register_blueprint(blogs_bp, url_prefix='/main')

    
    @blogs_bp.route('/blogs/communities/create', methods=['POST'])
    @login_required
    def create_community():
        data = request.json
        name = data.get('name')
        description = data.get('description')
        banner_url = data.get('banner_url')
        tag = data.get('tag')

        if not (name and description and tag):
            return jsonify({'error': 'All fields are required'}), 400

        community = Community(
            name=name,
            description=description,
            banner_url=banner_url,
            tag=tag,
            created_by=current_user.id
        )
        db.session.add(community)
        db.session.commit()

        return jsonify({'message': 'Community created successfully', 'community_id': community.id})

    @blogs_bp.route('/blogs/communities/<int:community_id>/join', methods=['POST'])
    @login_required
    def join_community(community_id):
        community = Community.query.get_or_404(community_id)
        if current_user in community.members:
            return jsonify({'error': 'You are already a member of this community'}), 400
        community.members.append(current_user)
        db.session.commit()
        return jsonify({'message': 'You have successfully joined the community'})

    
    @blogs_bp.route('/blogs/communities', methods=['GET'])
    @login_required
    def list_communities():
        user_tag = current_user.smile_reason
        communities = Community.query.filter_by(tag=user_tag).all()

        communities_data = [
            {
                'id': community.id,
                'name': community.name,
                'description': community.description,
                'banner_url': community.banner_url,
                'members_count': len(community.members),
            }
            for community in communities
        ]
        return jsonify(communities_data)

    # Create a new blog
    @blogs_bp.route('/blogs/create', methods=['POST'])
    @login_required
    def create_blog():
        data = request.json
        community_id = data.get('community_id')
        title = data.get('title')
        content = data.get('content')

        if not (community_id and title and content):
            return jsonify({'error': 'All fields are required'}), 400

        community = Community.query.get_or_404(community_id)

        # Check if the user is a member of the community
        if current_user not in community.members:
            return jsonify({'error': 'You must be a member of this community to post a blog'}), 403

        blog = Blog(
            title=title,
            content=content,
            community_id=community_id,
            created_by=current_user.id
        )
        db.session.add(blog)
        db.session.commit()
        return jsonify({'message': 'Blog created successfully', 'blog_id': blog.id})

    # Add a comment to a blog
    @blogs_bp.route('/blogs/<int:blog_id>/comments', methods=['POST'])
    @login_required
    def add_comment(blog_id):
        data = request.json
        content = data.get('content')
        image_url = data.get('image_url', None)

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        blog = Blog.query.get_or_404(blog_id)

        comment = Comment(
            content=content,
            image_url=image_url,
            blog_id=blog_id,
            created_by=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully', 'comment_id': comment.id})

    # Get all comments for a blog
    @blogs_bp.route('/blogs/<int:blog_id>/comments', methods=['GET'])
    @login_required
    def get_comments(blog_id):
        blog = Blog.query.get_or_404(blog_id)
        comments = Comment.query.filter_by(blog_id=blog.id).all()

        comments_data = [
            {
                'comment_id': comment.id,
                'content': comment.content,
                'image_url': comment.image_url,
                'created_by': User.query.get(comment.created_by).name
            }
            for comment in comments
        ]
        return jsonify({'comments': comments_data})

    # Display all blogs of the user's community
    @blogs_bp.route('/blogs', methods=['GET'])
    @login_required
    def display_blogs():
        user_tag = current_user.smile_reason
        communities = Community.query.filter_by(tag=user_tag).all()
        blogs_data = []

        for community in communities:
            blogs = Blog.query.filter_by(community_id=community.id).all()
            for blog in blogs:
                comments = Comment.query.filter_by(blog_id=blog.id).all()
                blogs_data.append({
                    'blog_id': blog.id,
                    'title': blog.title,
                    'content': blog.content,
                    'created_by': User.query.get(blog.created_by).name,
                    'community_name': community.name,
                    'likes': blog.likes,
                    'dislikes': blog.dislikes,
                    'comments': [
                        {
                            'comment_id': comment.id,
                            'content': comment.content,
                            'image_url': comment.image_url,
                            'created_by': User.query.get(comment.created_by).name
                        }
                        for comment in comments
                    ]
                })
        return jsonify({'blogs': blogs_data})

    # Get the list of online users
    @blogs_bp.route('/online-users', methods=['GET'])
    @login_required
    def online_users():
        online_users = get_online_users()
        return jsonify({'online_users': online_users})
