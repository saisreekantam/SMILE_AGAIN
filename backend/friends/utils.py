from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from models import Message, User, Friendship, FriendRequest
from extensions import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FriendshipManager:
    """
    A comprehensive utility class for managing friend relationships and requests
    """
    
    def __init__(self):
        self.db = db
        
    def get_friend_suggestions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get friend suggestions based on mutual friends and user interests
        
        Args:
            user_id (int): The ID of the user
            limit (int): Maximum number of suggestions to return
            
        Returns:
            List[Dict]: List of suggested friends with their details and matching criteria
        """
        try:
            # Get current user's friends
            current_friends = set(
                friendship.friend_id 
                for friendship in Friendship.query.filter_by(
                    user_id=user_id, 
                    status='accepted'
                ).all()
            )
            
            # Get friends of friends
            friends_of_friends = set()
            for friend_id in current_friends:
                friend_friends = set(
                    friendship.friend_id 
                    for friendship in Friendship.query.filter_by(
                        user_id=friend_id, 
                        status='accepted'
                    ).all()
                )
                friends_of_friends.update(friend_friends)
            
            # Remove current user and their direct friends from suggestions
            friends_of_friends.discard(user_id)
            friends_of_friends.difference_update(current_friends)
            
            # Get user details and calculate mutual friend counts
            suggestions = []
            for potential_friend_id in friends_of_friends:
                mutual_friends = self.get_mutual_friends(user_id, potential_friend_id)
                potential_friend = User.query.get(potential_friend_id)
                
                if potential_friend:
                    suggestions.append({
                        'id': potential_friend.id,
                        'name': potential_friend.name,
                        'mutual_friends_count': len(mutual_friends),
                        'mutual_friends': mutual_friends[:5],  # List first 5 mutual friends
                        'registered_since': potential_friend.created_at.isoformat()
                    })
            
            # Sort by number of mutual friends and limit results
            suggestions.sort(key=lambda x: x['mutual_friends_count'], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting friend suggestions: {str(e)}")
            return []

    def get_friendship_statistics(self, user_id: int) -> Dict:
        """
        Get comprehensive statistics about a user's friendships
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            Dict: Dictionary containing various friendship statistics
        """
        try:
            # Get all friendships
            friendships = Friendship.query.filter_by(
                user_id=user_id,
                status='accepted'
            ).all()
            
            # Calculate statistics
            stats = {
                'total_friends': len(friendships),
                'friends_added_this_month': sum(
                    1 for f in friendships 
                    if f.created_at >= datetime.utcnow() - timedelta(days=30)
                ),
                'pending_sent_requests': FriendRequest.query.filter_by(
                    sender_id=user_id,
                    status='pending'
                ).count(),
                'pending_received_requests': FriendRequest.query.filter_by(
                    recipient_id=user_id,
                    status='pending'
                ).count(),
                'most_active_friends': self._get_most_active_friends(user_id, limit=5)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting friendship statistics: {str(e)}")
            return {}

    def _get_most_active_friends(self, user_id: int, limit: int = 5) -> List[Dict]:
        """
        Get the most active friends based on interaction frequency
        
        Args:
            user_id (int): The ID of the user
            limit (int): Maximum number of friends to return
            
        Returns:
            List[Dict]: List of most active friends with their activity details
        """
        try:
            # Get all accepted friendships
            friends = Friendship.query.filter_by(
                user_id=user_id,
                status='accepted'
            ).all()
            
            friend_activity = []
            for friendship in friends:
                friend = User.query.get(friendship.friend_id)
                if friend:
                    # Calculate interaction metrics (customize based on your needs)
                    activity_score = self._calculate_friend_activity_score(
                        user_id, 
                        friendship.friend_id
                    )
                    
                    friend_activity.append({
                        'id': friend.id,
                        'name': friend.name,
                        'activity_score': activity_score,
                        'last_interaction': friendship.updated_at.isoformat(),
                        'friendship_duration': (
                            datetime.utcnow() - friendship.created_at
                        ).days
                    })
            
            # Sort by activity score and return top N
            friend_activity.sort(key=lambda x: x['activity_score'], reverse=True)
            return friend_activity[:limit]
            
        except Exception as e:
            logger.error(f"Error getting most active friends: {str(e)}")
            return []

    def _calculate_friend_activity_score(self, user_id: int, friend_id: int) -> float:
        """
        Calculate an activity score for a friendship based on various metrics
        
        Args:
            user_id (int): The ID of the user
            friend_id (int): The ID of the friend
            
        Returns:
            float: Activity score between 0 and 1
        """
        try:
            # This is a placeholder implementation
            # Customize based on your specific needs and available data
            
            # Example factors that could contribute to the score:
            # - Number of messages exchanged
            # - Frequency of interactions
            # - Shared group memberships
            # - Recent activity
            
            # Placeholder implementation
            message_count = Message.query.filter(
                or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == friend_id),
                    and_(Message.sender_id == friend_id, Message.receiver_id == user_id)
                )
            ).count()
            
            # Normalize the score between 0 and 1
            # This is a simple example - enhance based on your needs
            score = min(message_count / 100.0, 1.0)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating friend activity score: {str(e)}")
            return 0.0

    def handle_friend_request_notification(self, request: FriendRequest) -> Dict:
        """
        Generate notification data for a friend request
        
        Args:
            request (FriendRequest): The friend request object
            
        Returns:
            Dict: Notification data for the request
        """
        try:
            sender = User.query.get(request.sender_id)
            recipient = User.query.get(request.recipient_id)
            
            if not sender or not recipient:
                return {}
                
            notification_data = {
                'type': 'friend_request',
                'request_id': request.id,
                'sender': {
                    'id': sender.id,
                    'name': sender.name
                },
                'recipient': {
                    'id': recipient.id,
                    'name': recipient.name
                },
                'message': request.message,
                'created_at': request.created_at.isoformat(),
                'mutual_friends': self.get_mutual_friends(
                    request.sender_id,
                    request.recipient_id
                )
            }
            
            return notification_data
            
        except Exception as e:
            logger.error(f"Error generating friend request notification: {str(e)}")
            return {}
