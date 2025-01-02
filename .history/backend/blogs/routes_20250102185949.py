from flask import request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Community, Blog, User, Comment
from .utils import admin_required, get_online_users

def register_routes(app, main_bp):
    app.register_blueprint(main_bp, url_prefix='/main')

    @main_bp.route('/communities/create', methods=['POST'])
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

    @main_bp.route('/communities', methods=['GET'])
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

    @main_bp.route('/communities/<int:community_id>/join', methods=['POST'])
    @login_required
    def join_community(community_id):
        community = Community.query.get_or_404(community_id)

        if current_user in community.members:
            return jsonify({'error': 'You are already a member of this community'}), 400

        community.members.append(current_user)
        db.session.commit()
        return jsonify({'message': 'Joined community successfully'})

    @main_bp.route('/blogs/create', methods=['POST'])
    @login_required
    def create_blog():
        data = request.json
        community_id = data.get('community_id')
        title = data.get('title')
        content = data.get('content')

        if not (community_id and title and content):
            return jsonify({'error': 'All fields are required'}), 400

        community = Community.query.get_or_404(community_id)
        if current_user not in community.members:
            return jsonify({'error': 'You must be a member of this community to post'}), 403

        blog = Blog(
            title=title,
            content=content,
            community_id=community_id,
            created_by=current_user.id
        )
        db.session.add(blog)
        db.session.commit()
        return jsonify({'message': 'Blog created successfully', 'blog_id': blog.id})

    @main_bp.route('/blogs/<int:blog_id>/comments', methods=['POST'])
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

    @main_bp.route('/people-you-may-know', methods=['GET'])
    @login_required
    def people_you_may_know():
        user_tag = current_user.smile_reason
        users = User.query.filter_by(smile_reason=user_tag).all()

        users_data = [
            {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'online': user.is_online,
            }
            for user in users if user.id != current_user.id
        ]
        return jsonify(users_data)

    @main_bp.route('/online-users', methods=['GET'])
    @login_required
    def online_users():
        online_users = get_online_users()
        return jsonify({'online_users': online_users})
