from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import StressAssessment, db
stress_bp = Blueprint('stress', __name__)

@stress_bp.route('/assessment', methods=['POST'])
@login_required
def submit_assessment():
    try:
        data = request.json
        
        # Calculate stress score based on responses
        stress_score = calculate_stress_score(data)
        
        # Generate recommendations
        recommendations = generate_recommendations(stress_score, data)
        
        # Save assessment
        assessment = StressAssessment(
            user_id=current_user.id,
            stress_score=stress_score,
            sleep_quality=data.get('sleep_quality'),
            anxiety_level=data.get('anxiety_level'),
            social_support=data.get('social_support'),
            work_stress=data.get('work_stress'),
            physical_activity=data.get('physical_activity'),
            mood_rating=data.get('mood_rating'),
            recommendations=recommendations
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        # Send email report
        send_stress_report(current_user.email, assessment)
        
        return jsonify({
            'message': 'Assessment submitted successfully',
            'stress_score': stress_score,
            'recommendations': recommendations
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_stress_score(data):
    weights = {
        'sleep_quality': 0.2,
        'anxiety_level': 0.25,
        'social_support': 0.15,
        'work_stress': 0.2,
        'physical_activity': 0.1,
        'mood_rating': 0.1
    }
    
    score = sum(data[key] * weights[key] for key in weights)
    normalized_score = (score / 5) * 100  # Convert to 0-100 scale
    return round(normalized_score, 2)

def generate_recommendations(stress_score, data):
    recommendations = []
    
    if stress_score > 70:
        recommendations.append("Consider speaking with a mental health professional")
        
    if data['sleep_quality'] < 3:
        recommendations.append("Try to improve sleep hygiene by maintaining a consistent sleep schedule")
        
    if data['physical_activity'] < 3:
        recommendations.append("Incorporate more physical activity into your daily routine")
        
    if data['social_support'] < 3:
        recommendations.append("Reach out to friends or join community groups for social support")
        
    return "\n".join(recommendations)

def send_stress_report(email, assessment):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your-email@gmail.com"  # Configure with your email
    sender_password = "your-app-password"   # Use app-specific password
    
    msg = MIMEMultipart()
    msg["Subject"] = f"Your Weekly Stress Assessment Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = sender_email
    msg["To"] = email
    
    # Create HTML email content
    html_content = f"""
    <html>
        <body>
            <h2>Your Weekly Stress Assessment Report</h2>
            <p>Assessment Date: {assessment.assessment_date.strftime('%Y-%m-%d')}</p>
            <h3>Results:</h3>
            <ul>
                <li>Overall Stress Score: {assessment.stress_score}/100</li>
                <li>Sleep Quality: {assessment.sleep_quality}/5</li>
                <li>Anxiety Level: {assessment.anxiety_level}/5</li>
                <li>Social Support: {assessment.social_support}/5</li>
                <li>Work Stress: {assessment.work_stress}/5</li>
                <li>Physical Activity: {assessment.physical_activity}/5</li>
                <li>Mood Rating: {assessment.mood_rating}/5</li>
            </ul>
            <h3>Recommendations:</h3>
            <p>{assessment.recommendations}</p>
            <p>Remember, help is always available. Don't hesitate to reach out to professionals or loved ones.</p>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        assessment.email_sent = True
        db.session.commit()
        
    except Exception as e:
        print(f"Failed to send email: {e}")