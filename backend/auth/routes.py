from flask import request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import User, SessionLog, UserProblem
from .utils import hash_password, check_password
from flask import make_response

def register_routes(bp, db, bcrypt, login_manager):
    """Register routes with the blueprint"""
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @bp.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            print("Received data:", data)  # Debug print
            
            if not all(key in data for key in ['name', 'email', 'password', 'gender']):
                return jsonify({'error': 'Missing required fields'}), 400
                
            hashed_password = hash_password(bcrypt, data['password'])
            user = User(
                name=data['name'],
                email=data['email'],
                password=hashed_password,
                gender=data['gender']
            )
            db.session.add(user)
            db.session.commit()
         
            return jsonify({'message': 'User registered successfully'}), 201
            
        except Exception as e:
            print("Registration error:", str(e))  # Debug print
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(email=data['email']).first()

        if user and check_password(bcrypt, user.password, data['password']):
            login_user(user)
            new_session = SessionLog(user_id=user.id)
            db.session.add(new_session)
            db.session.commit()

            # Respond with a success flag and user details (if needed)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user_id': user.id,  # Optional: Include user details if needed
                'username': user.name  # Example
            }), 200

        # Respond with an error if login fails
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    
    @bp.route('/google-login', methods=['POST'])
    def google_login():
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            user = User(
                name=data['name'],
                email=data['email'],
                password=hash_password(bcrypt, 'google_login'),
                gender='Not specified'
            )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        new_session = SessionLog(user_id=user.id)
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('auth.problem_page'))
    
    @bp.route('/problem-page', methods=['GET', 'POST', 'OPTIONS'])
    @login_required
    def problem_page():
        print("Request method:", request.method)  # Debug print

        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')  # Allow your frontend origin
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Credentials', 'true')  # Must be 'true'
            return response, 200  # Ensure correct status code

        elif request.method == 'POST':
            data = request.json
            print("POST data received:", data)  # Debug print

            problem = UserProblem.query.filter_by(user_id=current_user.id).first()

            if not problem:
                problem = UserProblem(
                    user_id=current_user.id,
                    smile_last_time=data.get('smile_last_time', ''),
                    smile_reason=data.get('smile_reason', '')
                )
                db.session.add(problem)
            else:
                problem.smile_last_time = data.get('smile_last_time', problem.smile_last_time)
                problem.smile_reason = data.get('smile_reason', problem.smile_reason)

            db.session.commit()
            response = jsonify({'message': 'Answer saved successfully'})
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')  # Allow your frontend origin
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200

        elif request.method == 'GET':
            problem = UserProblem.query.filter_by(user_id=current_user.id).first()
            response = jsonify({
                'smile_last_time': problem.smile_last_time if problem else '',
                'smile_reason': problem.smile_reason if problem else ''
            })
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')  # Allow your frontend origin
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200

        # Default case for unsupported methods
        return jsonify({'error': 'Method not allowed'}), 405
    @bp.route('/update-smile-reason', methods=['POST'])
    @login_required
    def update_smile_reason():
        data = request.json
        problem = UserProblem.query.filter_by(user_id=current_user.id).first()
        if problem:
            problem.smile_reason = data['smile_reason']
            db.session.commit()
            return jsonify({'message': 'Smile reason updated successfully'})
        return jsonify({'message': 'Problem data not found'}), 404

    @bp.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'})