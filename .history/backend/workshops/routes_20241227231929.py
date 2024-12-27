from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import Workshop, User
from backend.app import db
from workshops.utils import admin_required
import smtplib
from email.mime.text import MIMEText

workshops_bp = Blueprint('workshops', __name__)


def send_email(to, subject, body):
    smtp_server = "" 
    smtp_port = 587
    sender_email = "jupalliprabhas@gmail.com"
    sender_password = "your_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import Workshop, Feedback, User
from backend.app import db
from workshops.utils import admin_required, send_email

workshops_bp = Blueprint('workshops', __name__)

# Route to create a workshop
@workshops_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create_workshop():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    banner_url = data.get('banner_url')
    meet_link = data.get('meet_link')
    price = data.get('price', 0.0)
    sponsored = data.get('sponsored', False)
    tag = data.get('tag')

    if not (title and description and banner_url and meet_link and tag):
        return jsonify({'error': 'All fields are required'}), 400

    new_workshop = Workshop(
        title=title,
        description=description,
        banner_url=banner_url,
        meet_link=meet_link,
        price=price,
        is_paid=(price > 0),
        sponsored=sponsored,
        tag=tag,
        created_by=current_user.id
    )
    db.session.add(new_workshop)
    db.session.commit()
    return jsonify({'message': 'Workshop created successfully', 'workshop_id': new_workshop.id})


# Route to list workshops
@workshops_bp.route('/list', methods=['GET'])
@login_required
def list_workshops():
    smile_reason = current_user.smile_reason
    workshops = Workshop.query.filter_by(tag=smile_reason).order_by(
        Workshop.sponsored.desc(),
        Workshop.id.desc()
    ).all()

    workshops_data = []
    for workshop in workshops:
        feedback_list = Feedback.query.filter_by(workshop_id=workshop.id).all()
        avg_rating = sum(f.rating for f in feedback_list) / len(feedback_list) if feedback_list else None

        workshops_data.append({
            'id': workshop.id,
            'title': workshop.title,
            'description': workshop.description,
            'banner_url': workshop.banner_url,
            'meet_link': workshop.meet_link if not workshop.is_paid else None,
            'is_paid': workshop.is_paid,
            'price': workshop.price,
            'sponsored': workshop.sponsored,
            'tag': workshop.tag,
            'created_by': User.query.get(workshop.created_by).name,
            'average_rating': avg_rating
        })

    return jsonify(workshops_data)


# Route to promote a workshop
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


# Route to delete a workshop
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


# Route to handle payments
@workshops_bp.route('/pay/<int:workshop_id>', methods=['POST'])
@login_required
def pay_for_workshop(workshop_id):
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    if not workshop.is_paid:
        return jsonify({'error': 'This workshop is free'}), 400

   
    workshop.meet_link = 'https://secure.meetlink.com/' + str(workshop_id)  # Example secured link
    db.session.commit()

    # Send email with meet link
    send_email(
        recipient=current_user.email,
        subject=f"Workshop Access: {workshop.title}",
        body=f"Thank you for paying! Your access link is: {workshop.meet_link}"
    )
    return jsonify({'message': 'Payment successful. Meet link sent to your email'})


# Route to submit feedback
@workshops_bp.route('/feedback/<int:workshop_id>', methods=['POST'])
@login_required
def submit_feedback(workshop_id):
    data = request.json
    comments = data.get('comments')
    rating = data.get('rating')

    if not (comments and rating):
        return jsonify({'error': 'Comments and rating are required'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    existing_feedback = Feedback.query.filter_by(workshop_id=workshop_id, user_id=current_user.id).first()
    if existing_feedback:
        return jsonify({'error': 'You have already submitted feedback for this workshop'}), 400

    feedback = Feedback(
        workshop_id=workshop_id,
        user_id=current_user.id,
        comments=comments,
        rating=rating
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback submitted successfully'})


# Route to view feedback
@workshops_bp.route('/feedback/<int:workshop_id>', methods=['GET'])
@login_required
@admin_required
def view_feedback(workshop_id):
    workshop = Workshop.query.get(workshop_id)
    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    feedback_list = Feedback.query.filter_by(workshop_id=workshop_id).all()
    feedback_data = [
        {
            'user': User.query.get(feedback.user_id).name,
            'comments': feedback.comments,
            'rating': feedback.rating,
            'timestamp': feedback.timestamp
        }
        for feedback in feedback_list
    ]
    return jsonify({'workshop_title': workshop.title, 'feedback': feedback_data})
