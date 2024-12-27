from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Workshop, User
from wor.utils import admin_required

workshops_bp = Blueprint('workshops', __name__)

@workshops_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create_workshop():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    banner_url = data.get('banner_url')
    meet_link = data.get('meet_link')
    is_paid = data.get('is_paid', False)
    sponsored = data.get('sponsored', False)
    tag = data.get('tag')

    if not (title and description and banner_url and meet_link and tag):
        return jsonify({'error': 'All fields are required'}), 400

    new_workshop = Workshop(
        title=title,
        description=description,
        banner_url=banner_url,
        meet_link=meet_link,
        is_paid=is_paid,
        sponsored=sponsored,
        tag=tag,
        created_by=current_user.id
    )
    db.session.add(new_workshop)
    db.session.commit()
    return jsonify({'message': 'Workshop created successfully', 'workshop_id': new_workshop.id})

@workshops_bp.route('/list', methods=['GET'])
@login_required
def list_workshops():
    smile_reason = current_user.smile_reason
    matching_workshops = Workshop.query.filter_by(tag=smile_reason).all()
    workshops_data = [
        {
            'id': workshop.id,
            'title': workshop.title,
            'description': workshop.description,
            'banner_url': workshop.banner_url,
            'meet_link': workshop.meet_link,
            'is_paid': workshop.is_paid,
            'sponsored': workshop.sponsored,
            'tag': workshop.tag,
            'created_by': User.query.get(workshop.created_by).name
        }
        for workshop in matching_workshops
    ]
    return jsonify(workshops_data)

@workshops_bp.route('/promote/<int:workshop_id>', methods=['POST'])
@login_required
@admin_required
def promote_workshop(workshop_id):
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    workshop.sponsored = True
    db.session.commit()
    return jsonify({'message': 'Workshop promoted successfully'})

@workshops_bp.route('/delete/<int:workshop_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_workshop(workshop_id):
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    db.session.delete(workshop)
    db.session.commit()
    return jsonify({'message': 'Workshop deleted successfully'})
