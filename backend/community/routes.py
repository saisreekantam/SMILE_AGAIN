from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Community, CommunityPost, CommunityComment, UserProblem, User
from extensions import db
from datetime import datetime

community_bp = Blueprint('community', __name__)

def register_community_routes(bp, db):
    @bp.route('/communities', methods=['GET'])
    @login_required
    def get_communities():
        try:
            # Get user's smile reason
            user_problem = UserProblem.query.filter_by(user_id=current_user.id).first()
            if not user_problem or not user_problem.smile_reason:
                return jsonify({'error': 'Please set your smile reason first'}), 400

            community = Community.query.filter_by(smile_reason=user_problem.smile_reason).first()
            
            if not community:
                community = Community(
                    name=f"{user_problem.smile_reason} Community",
                    description=f"A community for people who smile because of {user_problem.smile_reason}",
                    smile_reason=user_problem.smile_reason
                )
                db.session.add(community)
                db.session.commit()

            # Add user to community if not already a member
            if current_user not in community.members:
                community.members.append(current_user)
                db.session.commit()

            # Get community details with member count
            return jsonify({
                'id': community.id,
                'name': community.name,
                'description': community.description,
                'member_count': len(community.members),
                'created_at': community.created_at.isoformat()
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/communities/<int:community_id>/posts', methods=['GET', 'POST'])
    @login_required
    def community_posts(community_id):
        try:
            community = Community.query.get_or_404(community_id)
            
            # Verify user is a member
            if current_user not in community.members:
                return jsonify({'error': 'You are not a member of this community'}), 403

            if request.method == 'GET':
                # Get posts with pagination
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                
                posts = CommunityPost.query.filter_by(community_id=community_id)\
                    .order_by(CommunityPost.created_at.desc())\
                    .paginate(page=page, per_page=per_page)

                return jsonify({
                    'posts': [{
                        'id': post.id,
                        'content': post.content,
                        'author': post.author.name,
                        'likes': post.likes,
                        'created_at': post.created_at.isoformat(),
                        'comment_count': len(post.comments)
                    } for post in posts.items],
                    'total_pages': posts.pages,
                    'current_page': posts.page
                })

            # Handle POST request
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400

            new_post = CommunityPost(
                community_id=community_id,
                user_id=current_user.id,
                content=data['content']
            )
            db.session.add(new_post)
            db.session.commit()

            return jsonify({
                'message': 'Post created successfully',
                'post_id': new_post.id
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/posts/<int:post_id>/comments', methods=['GET', 'POST'])
    @login_required
    def post_comments(post_id):
        try:
            post = CommunityPost.query.get_or_404(post_id)
            
            if request.method == 'GET':
                comments = CommunityComment.query.filter_by(post_id=post_id)\
                    .order_by(CommunityComment.created_at).all()
                    
                return jsonify([{
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.name,
                    'created_at': comment.created_at.isoformat()
                } for comment in comments])

            # Handle POST request
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400

            new_comment = CommunityComment(
                post_id=post_id,
                user_id=current_user.id,
                content=data['content']
            )
            db.session.add(new_comment)
            db.session.commit()

            return jsonify({
                'message': 'Comment added successfully',
                'comment_id': new_comment.id
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/posts/<int:post_id>/like', methods=['POST'])
    @login_required
    def like_post(post_id):
        try:
            post = CommunityPost.query.get_or_404(post_id)
            post.likes += 1
            db.session.commit()
            
            return jsonify({
                'message': 'Post liked successfully',
                'new_like_count': post.likes
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/communities/<int:community_id>/members', methods=['GET'])
    @login_required
    def get_community_members(community_id):
        try:
            community = Community.query.get_or_404(community_id)
            
            if current_user not in community.members:
                return jsonify({'error': 'You are not a member of this community'}), 403

            return jsonify([{
                'id': member.id,
                'name': member.name,
                'joined_at': member.created_at.isoformat()
            } for member in community.members])

        except Exception as e:
            return jsonify({'error': str(e)}), 500