from flask import request, jsonify
from flask_login import login_required, current_user
from backend.models import  Group, group_members,User


def chat_routes(chats_bp, db, socketio):
    @chats_bp.route('/active', methods=['GET'])
    @login_required
    def active_users():
        active_users = User.query.filter(User.is_online == True).all()
        active_list = [{'id': user.id, 'name': user.name} for user in active_users]
        return jsonify(active_list)

    @chats_bp.route('/groups', methods=['GET', 'POST'])
    @login_required
    def groups():
        if request.method == 'GET':
            user_groups = Group.query.join(group_members).filter(group_members.c.user_id == current_user.id).all()
            group_list = [{'id': group.id, 'name': group.name, 'created_by': group.created_by} for group in user_groups]
            return jsonify(group_list)

        data = request.json
        new_group = Group(name=data['name'], created_by=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        db.session.execute(group_members.insert().values(group_id=new_group.id, user_id=current_user.id))
        db.session.commit()
        return jsonify({'message': 'Group created successfully', 'group_id': new_group.id})

    @chats_bp.route('/groups/<int:group_id>/add', methods=['POST'])
    @login_required
    def add_to_group(group_id):
        data = request.json
        friend_id = data.get('friend_id')
        friend = User.query.get(friend_id)
        group = Group.query.get(group_id)

        if not group or group.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized or group not found'}), 403

        if friend_id and friend in current_user.friends:  # Assuming `friends` is a relationship on User
            db.session.execute(group_members.insert().values(group_id=group_id, user_id=friend_id))
            db.session.commit()
            return jsonify({'message': f'{friend.name} added to the group'})
        return jsonify({'error': 'Friend not found or not authorized'}), 404

    @chats_bp.route('/groups/<int:group_id>/request', methods=['POST'])
    @login_required
    def request_to_join(group_id):
        group = Group.query.get(group_id)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        
        return jsonify({'message': 'Request to join sent to the group creator'})

    @chats_bp.route('/groups/<int:group_id>/leave', methods=['POST'])
    @login_required
    def leave_group(group_id):
        group = Group.query.get(group_id)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        if current_user.id in [member.id for member in group.members]:
            db.session.execute(group_members.delete().where(
                (group_members.c.group_id == group_id) &
                (group_members.c.user_id == current_user.id)
            ))
            db.session.commit()
            return jsonify({'message': 'You have left the group'})
        return jsonify({'error': 'You are not a member of this group'}), 403

    @chats_bp.route('/groups/<int:group_id>/remove', methods=['POST'])
    @login_required
    def remove_from_group(group_id):
        data = request.json
        user_id = data.get('user_id')
        user = User.query.get(user_id)
        group = Group.query.get(group_id)

        if not group or group.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized or group not found'}), 403

        if user and user in group.members:
            db.session.execute(group_members.delete().where(
                (group_members.c.group_id == group_id) &
                (group_members.c.user_id == user_id)
            ))
            db.session.commit()
            return jsonify({'message': f'{user.name} removed from the group'})
        return jsonify({'error': 'User not found or not a member of the group'}), 40