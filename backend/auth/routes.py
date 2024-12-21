from flask import request, jsonify, session, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import User,SessionLog,UserProblem
from .utils import hash_password, check_password

def auth_routes(auth_bp, db, bcrypt, login_manager):
    @auth_bp.route('/register', methods=['POST'])
    def register():
        data = request.json
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

    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password(bcrypt, user.password, data['password']):
            login_user(user)
            new_session = SessionLog(user_id=user.id)
            db.session.add(new_session)
            db.session.commit()
            return redirect(url_for('auth.problem_page'))
        return jsonify({'message': 'Invalid credentials'}), 401

    @auth_bp.route('/google-login', methods=['POST'])
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

    @auth_bp.route('/problem-page', methods=['GET', 'POST'])
    @login_required
    def problem_page():
        if request.method == 'GET':
            problem = UserProblem.query.filter_by(user_id=current_user.id).first()
            return jsonify({
                'smile_last_time': problem.smile_last_time if problem else '',
                'smile_reason': problem.smile_reason if problem else ''
            })

        data = request.json
        problem = UserProblem.query.filter_by(user_id=current_user.id).first()
        if not problem:
            problem = UserProblem(user_id=current_user.id, smile_last_time=data['smile_last_time'])
        else:
            problem.smile_last_time = data['smile_last_time']
        db.session.add(problem)
        db.session.commit()
        return jsonify({'message': 'Answer saved successfully'})

    @auth_bp.route('/update-smile-reason', methods=['POST'])
    @login_required
    def update_smile_reason():
        data = request.json
        problem = UserProblem.query.filter_by(user_id=current_user.id).first()
        if problem:
            problem.smile_reason = data['smile_reason']
            db.session.commit()
            return jsonify({'message': 'Smile reason updated successfully'})
        return jsonify({'message': 'Problem data not found'}), 404

    @auth_bp.route('/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
