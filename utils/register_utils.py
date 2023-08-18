from typing import Tuple
import bcrypt
from email_validator import validate_email, EmailNotValidError
import logging
from db import db_pool
from password_strength import PasswordPolicy


def validate_input(
    email: str, password: str, name: str, diet_type: str, daily_budget: float
) -> Tuple[bool, str]:
    if not all([email, password, name, diet_type, daily_budget]):
        return (False, "Missing fields in registration data")

    # Check if the email is valid
    if not is_valid_email(email):
        return (False, "Invalid email address")

    if not pw_strong_enough(password):
        return (False, "Password is not strong enough")
    # Check if the daily_budget is a positive number
    try:
        daily_budget = float(daily_budget)
        if daily_budget <= 0:
            return (False, "Daily budget must be a positive number")

    except ValueError:
        return (False, "Invalid daily budget value")

    return (True, "Valid input data")


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    # Convert the hashed password to a string before storing
    hashed_password = hashed_password.decode("utf-8")

    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def is_valid_email(email) -> bool:
    try:
        # Validate.
        v = validate_email(email)

        # Update with the normalized form.
        email = v["email"]
        return True
    except EmailNotValidError as e:
        # Email is not valid, handle exception or return False
        logging.warning(str(e))
        return False


def save_user_to_db(user) -> bool:
    db_connection = db_pool.pg_connection_pool.getconn()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute(
                "INSERT INTO public.users (email, password, name, diet_type, daily_budget) VALUES (%s, %s, %s, %s, %s)",
                (
                    user.email,
                    user.password,
                    user.username,
                    "default_diet_type",
                    100.0,
                ),
            )
            db_connection.commit()
            cursor.close()
            db_pool.pg_connection_pool.putconn(db_connection)
            return True
        except Exception as e:
            db_pool.pg_connection_pool.putconn(db_connection)
            logging.error(f"Exception while inserting user to database: {e}")
            return False


def check_user_exists(email: str) -> bool:
    db_connection = db_pool.pg_connection_pool.getconn()
    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM public.users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            return True if user else False
        except Exception as e:
            logging.error(f"Exception while checking user in database: {e}")
            return False
        finally:
            db_pool.pg_connection_pool.putconn(db_connection)


def pw_strong_enough(password: str) -> bool:
    policy = PasswordPolicy.from_names(
        length=10,  # min length: 10
        uppercase=1,  # need min. 1 uppercase letters
        numbers=1,  # need min. 1 digits
        nonletters=1,  # need min. 1 non-letter characters
    )
    logging.info(policy.test(password))
    return len(policy.test(password)) == 0


def authenticate_user(email: str, password: str) -> Tuple[bool, str]:
    user_exists = check_user_exists(email)
    if not user_exists:
        return (False, "User does not exist")
    else:
        db_connection = db_pool.pg_connection_pool.getconn()
        if db_connection:
            try:
                cursor = db_connection.cursor()
                cursor.execute(
                    "SELECT password FROM public.users WHERE email = %s", (email,)
                )
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
