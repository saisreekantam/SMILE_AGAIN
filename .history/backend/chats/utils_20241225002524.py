from 
def create_message(sender_id, receiver_id, content, group_id=None):
    return Message(sender_id=sender_id, receiver_id=receiver_id, content=content, group_id=group_id)
