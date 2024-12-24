from flask import request, jsonify
from flask_login import login_required, current_user
from backend.models import Message, Group, group_members


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
            group_list = [{'id': group.id, 'name': group.name} for group in user_groups]
            return jsonify(group_list)

        data = request.json
        new_group = Group(name=data['name'], created_by=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        db.session.execute(group_members.insert().values(group_id=new_group.id, user_id=current_user.id))
        db.session.commit()
        return jsonify({'message': 'Group created successfully', 'group_id': new_group.id})

    @chats_bp.route('/unread', methods=['GET'])
    @login_required
    def unread_messages():
        unread_msgs = Message.query.filter_by(receiver_id=current_user.id, is_read=False).order_by(Message.timestamp).all()
        unread_list = [{'sender': msg.sender_id, 'content': msg.content, 'timestamp': msg.timestamp} for msg in unread_msgs]
        return jsonify(unread_list)

    @chats_bp.route('/read/<int:message_id>', methods=['POST'])
    @login_required
    def mark_as_read(message_id):
        msg = Message.query.get(message_id)
        if msg and msg.receiver_id == current_user.id:
            msg.is_read = True
            db.session.commit()
            return jsonify({'message': 'Message marked as read'})
        return jsonify({'error': 'Message not found or unauthorized'}), 404
