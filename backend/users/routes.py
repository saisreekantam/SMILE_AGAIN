from flask import request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from models import Profile, Friendship, Blog, User

def register_routes(bp, db):
    """Register routes with the users blueprint"""
    
    @bp.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'GET':
            profile = Profile.query.filter_by(user_id=current_user.id).first()
            return jsonify({
                'name': current_user.name,
                'email': current_user.email,
                'gender': current_user.gender,
                'description': profile.description if profile else '',
                'profile_pic': profile.profile_pic if profile else url_for('static', filename='default.jpg')
            })

        data = request.form
        file = request.files.get('profile_pic')
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(f"{current_app.root_path}/static/{filename}")

        profile = Profile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            profile = Profile(
                user_id=current_user.id,
                description=data.get('description', ''),
                profile_pic=filename or 'static/default.jpg'
            )
            db.session.add(profile)
        else:
            profile.description = data.get('description', profile.description)
            profile.profile_pic = filename or profile.profile_pic
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})

    @bp.route('/friends', methods=['GET'])
    @login_required
    def friends():
    # Get friendships where user is either the requester or receiver
        friends = Friendship.query.filter(
        db.or_(
            db.and_(Friendship.user_id == current_user.id, Friendship.status == 'accepted'),
            db.and_(Friendship.friend_id == current_user.id, Friendship.status == 'accepted')
        )
    ).all()
    
        friend_list = []
        for friendship in friends:
        # If current user is the requester, add the friend
            if friendship.user_id == current_user.id:
                friend = User.query.get(friendship.friend_id)
                if friend:
                    friend_list.append({'id': friend.id, 'name': friend.name})
        # If current user is the receiver, add the requester
            else:
                friend = User.query.get(friendship.user_id)
                if friend:
                    friend_list.append({'id': friend.id, 'name': friend.name})
    
        return jsonify(friend_list)

    @bp.route('/friend/<int:friend_id>', methods=['POST'])
    @login_required
    def friend_action(friend_id):
        action = request.json.get('action')
        friendship = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend_id).first()
        if action == 'unfriend' and friendship:
            db.session.delete(friendship)
            db.session.commit()
            return jsonify({'message': 'Friend removed successfully'})
        return jsonify({'message': 'Invalid action'}), 400

    @bp.route('/blogs', methods=['GET', 'POST'])
    @login_required
    def blogs():
        if request.method == 'GET':
            blogs = Blog.query.filter_by(user_id=current_user.id).all()
            return jsonify([
                {'title': blog.title, 'content': blog.content}
                for blog in blogs
            ])
        
        # Handle POST request for creating a new blog
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Missing title or content'}), 400
            
        new_blog = Blog(
            user_id=current_user.id,
            title=data['title'],
            content=data['content']
        )
        db.session.add(new_blog)
        db.session.commit()
        
        return jsonify({'message': 'Blog created successfully'}), 201

    @bp.route('/blogs/<int:blog_id>', methods=['PUT', 'DELETE'])
    @login_required
    def manage_blog(blog_id):
        blog = Blog.query.filter_by(id=blog_id, user_id=current_user.id).first()
        if not blog:
            return jsonify({'error': 'Blog not found or unauthorized'}), 404

        if request.method == 'DELETE':
            db.session.delete(blog)
            db.session.commit()
            return jsonify({'message': 'Blog deleted successfully'})

        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        blog.title = data.get('title', blog.title)
        blog.content = data.get('content', blog.content)
        db.session.commit()
        
        return jsonify({'message': 'Blog updated successfully'})
