from flask import request, jsonify
from flask_login import login_required, current_user
from backend.models import Group, group_members, User, ChatRequest, Message
import nltk

nltk.download('stopwords')
nltk.download('punkt')

def contains_hate_speech(text):
    hate_words = ["hate", "kill", "abuse"]  
    tokens = nltk.word_tokenize(text.lower())
    return any(word in hate_words for word in tokens)

def register_routes(bp, db, socketio):
    """Register routes with the chats blueprint"""

    @bp.route('/active', methods=['GET'])
    @login_required
    def active_users():
        active_users = User.query.filter(User.is_online == True).all()
        active_list = [{'id': user.id, 'name': user.name} for user in active_users]
        return jsonify(active_list)

    @bp.route('/groups', methods=['GET', 'POST'])
    @login_required
    def groups():
        if request.method == 'GET':
            user_groups = Group.query.join(group_members).filter(
                group_members.c.user_id == current_user.id
            ).all()
            group_list = [{
                'id': group.id,
                'name': group.name,
                'created_by': group.created_by
            } for group in user_groups]
            return jsonify(group_list)

        data = request.json
        new_group = Group(name=data['name'], created_by=current_user.id)
        db.session.add(new_group)
        db.session.commit()
        
        db.session.execute(
            group_members.insert().values(
                group_id=new_group.id,
                user_id=current_user.id
            )
        )
        db.session.commit()
        
        return jsonify({
            'message': 'Group created successfully',
            'group_id': new_group.id
        })

    @bp.route('/groups/<int:group_id>/add', methods=['POST'])
    @login_required
    def add_to_group(group_id):
        data = request.json
        friend_id = data.get('friend_id')
        friend = User.query.get(friend_id)
        group = Group.query.get(group_id)

        if not group or group.created_by != current_user.id:
            return jsonify({
                'error': 'Unauthorized or group not found'
            }), 403

        if friend_id and friend in current_user.friends:
            db.session.execute(
                group_members.insert().values(
                    group_id=group_id,
                    user_id=friend_id
                )
            )
            db.session.commit()
            
            # Notify the group creator about the new member
            socketio.emit(
                'group_notification',
                {
                    'message': f'{friend.name} has joined the group {group.name}',
                    'group_id': group_id
                },
                to=group.created_by
            )
            
            return jsonify({'message': f'{friend.name} added to the group'})
            
        return jsonify({'error': 'Friend not found or not authorized'}), 404

    @bp.route('/groups/<int:group_id>/request', methods=['POST'])
    @login_required
    def request_to_join(group_id):
        group = Group.query.get(group_id)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        socketio.emit(
            'group_notification',
            {
                'message': f'{current_user.name} has requested to join the group {group.name}',
                'group_id': group_id
            },
            to=group.created_by
        )

        return jsonify({'message': 'Request to join sent to the group creator'})

    @bp.route('/groups/<int:group_id>/leave', methods=['POST'])
    @login_required
    def leave_group(group_id):
        group = Group.query.get(group_id)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        if current_user.id in [member.id for member in group.members]:
            db.session.execute(
                group_members.delete().where(
                    (group_members.c.group_id == group_id) & 
                    (group_members.c.user_id == current_user.id)
                )
            )
            db.session.commit()
            return jsonify({'message': 'You have left the group'})
            
        return jsonify({'error': 'You are not a member of this group'}), 403

    @bp.route('/groups/<int:group_id>/remove', methods=['POST'])
    @login_required
    def remove_from_group(group_id):
        data = request.json
        user_id = data.get('user_id')
        user = User.query.get(user_id)
        group = Group.query.get(group_id)

        if not group or group.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized or group not found'}), 403

        if user and user in group.members:
            db.session.execute(
                group_members.delete().where(
                    (group_members.c.group_id == group_id) & 
                    (group_members.c.user_id == user_id)
                )
            )
            db.session.commit()
            return jsonify({'message': f'{user.name} removed from the group'})
            
        return jsonify({'error': 'User not found or not a member of the group'}), 404

    @bp.route('/chat-request', methods=['POST'])
    @login_required
    def send_chat_request():
        data = request.json
        recipient_id = data.get('recipient_id')
        message_text = data.get('message')

        if not recipient_id or not message_text:
            return jsonify({'error': 'Recipient or message missing'}), 400

        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404

        # Check for hate language
        if contains_hate_speech(message_text):
            return jsonify({'error': 'Message contains inappropriate content'}), 403

        # Save chat request
        chat_request = ChatRequest(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            message=message_text
        )
        db.session.add(chat_request)
        db.session.commit()

        return jsonify({'message': 'Chat request sent successfully'})

    @bp.route('/chat-request/<int:request_id>/accept', methods=['POST'])
    @login_required
    def accept_chat_request(request_id):
        chat_request = ChatRequest.query.get(request_id)

        if not chat_request or chat_request.recipient_id != current_user.id:
            return jsonify({'error': 'Chat request not found or unauthorized'}), 403

        # Add as friends
        sender = User.query.get(chat_request.sender_id)
        current_user.friends.append(sender)
        db.session.commit()

        return jsonify({'message': f'{sender.name} is now your friend'})

    @bp.route('/chat-request/<int:request_id>/reject', methods=['POST'])
    @login_required
    def reject_chat_request(request_id):
        chat_request = ChatRequest.query.get(request_id)

        if not chat_request or chat_request.recipient_id != current_user.id:
            return jsonify({'error': 'Chat request not found or unauthorized'}), 403

        db.session.delete(chat_request)
        db.session.commit()

        return jsonify({'message': 'Chat request rejected'})

    @bp.route('/messages', methods=['POST'])
    @login_required
    def send_message():
        data = request.json
        recipient_id = data.get('recipient_id')
        message_text = data.get('message')

        if not recipient_id or not message_text:
            return jsonify({'error': 'Recipient or message missing'}), 400

        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404

        if contains_hate_speech(message_text):
            return jsonify({'error': 'Message contains inappropriate content'}), 403

        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=message_text
        )
        db.session.add(message)
        db.session.commit()

        return jsonify({'message': 'Message sent successfully'})

    @bp.route('/messages', methods=['GET'])
    @login_required
    def get_messages():
        messages = Message.query.filter_by(recipient_id=current_user.id).all()
        message_list = []

        for message in messages:
            message_list.append({
                'id': message.id,
                'sender': User.query.get(message.sender_id).name,
                'content': message.content,
                'timestamp': message.timestamp
            })

        return jsonify(message_list)
