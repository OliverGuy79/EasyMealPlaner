import jwt
import datetime
import os
import logging
from typing import Tuple
from db import db_pool
from utils.register_utils import check_user_exists
from utils.register_utils import check_password


# These would typically be stored securely in your environment, not hard-coded
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = 'HS256'

def generate_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }

    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_token



def refresh_google_token(refresh_token):
    # This is a mock function, but you would typically use the refresh token
    # to get a new access token from Google
    return "new_google_access_token"

def get_google_user_info(access_token):
    pass

def get_google_access_token(code):
    pass
    
    
def authenticate_user(email: str, password: str) -> Tuple[bool, str]:
    
    user_exists = check_user_exists(email)
    if not user_exists:
        return (False, "User does not exist")
    else:
        
        db_connection = db_pool.pg_connection_pool.getconn()
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute("SELECT password FROM public.users WHERE email = %s", (email,))
                hashed_password = cursor.fetchone()
                cursor.close()
                if hashed_password:
                    if check_password(password, hashed_password[0]):
                        return (True, "User authenticated")
                    else:
                        return (False, "Incorrect password")
                else:
                    return (False, "User does not exist")
            except Exception as e:
                logging.error(f"Exception while authenticating user: {e}")
                return (False, "Exception while authenticating user")
            finally:
                db_pool.pg_connection_pool.putconn(db_connection)