from backend
def is_friend(user_id, friend_id):
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id, status='accepted').first()
    return bool(friendship)
