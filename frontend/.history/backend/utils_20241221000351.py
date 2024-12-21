def hash_password(bcrypt, password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(bcrypt, hashed_password, plain_password):
    return bcrypt.check_password_hash(hashed_password, plain_password)
