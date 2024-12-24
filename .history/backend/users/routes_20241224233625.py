from flask import request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from .models import Profile, Friendship, Blog
from backend.auth. import user

def user_routes(users_bp, db):
    @users_bp.route('/profile', methods=['GET', 'POST'])
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
            profile = Profile(user_id=current_user.id, description=data.get('description', ''), profile_pic=filename or 'static/default.jpg')
            db.session.add(profile)
        else:
            profile.description = data.get('description', profile.description)
            profile.profile_pic = filename or profile.profile_pic
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})

    @users_bp.route('/friends', methods=['GET'])
    @login_required
    def friends():
        friends = Friendship.query.filter_by(user_id=current_user.id, status='accepted').all()
        friend_list = [{'id': friend.friend_id, 'name': User.query.get(friend.friend_id).name} for friend in friends]
        return jsonify(friend_list)

    @users_bp.route('/friend/<int:friend_id>', methods=['POST'])
    @login_required
    def friend_action(friend_id):
        action = request.json.get('action')
        friendship = Friendship.query.filter_by(user_id=current_user.id, friend_id=friend_id).first()
        if action == 'unfriend' and friendship:
            db.session.delete(friendship)
            db.session.commit()
            return jsonify({'message': 'Friend removed successfully'})
        return jsonify({'message': 'Invalid action'}), 400

    @users_bp.route('/blogs', methods=['GET', 'POST'])
    @login_required
    def blogs():
        if request.method == 'GET':
            blogs = Blog.query.filter_by(user_id=current_user.id).all()
            return jsonify([{'title': blog.title, 'content': blog.content} for blog in blogs])

        data = request.json
        blog = Blog(user_id=current_user.id, title=data['title'], content=data['content'])
        db.session.add(blog)
        db.session.commit()
        return jsonify({'message': 'Blog added successfully'})
