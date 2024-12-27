from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import Workshop, User
from backend.app import db
from workshops.utils import admin_required

workshops_bp = Blueprint('workshops', __name__)
import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    smtp_server = "smtp.example.com" 
    smtp_port = 587
    sender_email = ""
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
    price = data.get('price', 0.0)  # Default price is 0 for free workshops
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
        price=price,
        sponsored=sponsored,
        tag=tag,
        created_by=current_user.id
    )
    db.session.add(new_workshop)
    db.session.commit()
    return jsonify({'message': 'Workshop created successfully', 'workshop_id': new_workshop.id})


@workshops_bp.route('/update/<int:workshop_id>', methods=['PUT'])
@login_required
@admin_required
def update_workshop(workshop_id):
    data = request.json
    workshop = Workshop.query.get(workshop_id)

    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    workshop.title = data.get('title', workshop.title)
    workshop.description = data.get('description', workshop.description)
    workshop.banner_url = data.get('banner_url', workshop.banner_url)
    workshop.meet_link = data.get('meet_link', workshop.meet_link)
    workshop.is_paid = data.get('is_paid', workshop.is_paid)
    workshop.price = data.get('price', workshop.price)
    workshop.tag = data.get('tag', workshop.tag)
    db.session.commit()

    return jsonify({'message': 'Workshop updated successfully'})


@workshops_bp.route('/pay/<int:workshop_id>', methods=['POST'])
@login_required
def pay_for_workshop(workshop_id):
    workshop = Workshop.query.get(workshop_id)

    if not workshop:
        return jsonify({'error': 'Workshop not found'}), 404

    if not workshop.is_paid:
        return jsonify({'message': 'This workshop is free and does not require payment.'})

    # Payment logic (placeholder)
    payment_successful = True  # Replace with actual payment processing logic

    if payment_successful:
        # Send meeting password to the user's registered email
        password = "generated_password"  # Generate or retrieve the workshop password
        send_email(
            to=current_user.email,
            subject=f"Access to Workshop: {workshop.title}",
            body=f"Thank you for your payment. Here is the meeting password: {password}"
        )
        return jsonify({'message': 'Payment successful. Meeting password sent to your email.'})
    else:
        return jsonify({'error': 'Payment failed. Please try again.'}), 400


@workshops_bp.route('/list', methods=['GET'])
@login_required
def list_workshops():
    smile_reason = current_user.smile_reason
    matching_workshops = Workshop.query.filter_by(tag=smile_reason).order_by(
        Workshop.sponsored.desc(),  # Promoted workshops first
        Workshop.id.desc()          # Latest workshops next
    ).all()

    workshops_data = [
        {
            'id': workshop.id,
            'title': workshop.title,
            'description': workshop.description,
            'banner_url': workshop.banner_url,
            'meet_link': workshop.meet_link if not workshop.is_paid else None,  # Show link only for free workshops
            'is_paid': workshop.is_paid,
            'price': workshop.price,
            'sponsored': workshop.sponsored,
            'tag': workshop.tag,
            'created_by': User.query.get(workshop.created_by).name
        }
        for workshop in matching_workshops
    ]
    return jsonify(workshops_data)

