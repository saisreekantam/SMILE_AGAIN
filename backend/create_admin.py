from flask import current_app
from extensions import db
from models import User
from auth.utils import hash_password

def create_admin_user(app, email, password, name="Admin"):
    """
    Create an admin user or promote existing user to admin
    """
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Promote existing user to admin
            user.is_admin = True
            db.session.commit()
            print(f"User {email} promoted to admin")
        else:
            # Create new admin user
            hashed_password = hash_password(current_app.bcrypt, password)
            admin = User(
                name=name,
                email=email,
                password=hashed_password,
                is_admin=True,
                gender="Not specified"
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user {email} created successfully")

# Usage example:
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    create_admin_user(app, "k@example.com", "1234")