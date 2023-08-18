import azure.functions as func
import json
import logging
import utils.register_utils as register_utils
from models.user import User, UserEmailSignUp


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse the JSON request body
        req_body = req.get_json()
        new_user = UserEmailSignUp(**req_body)
        # Extract user details
        email = req_body.get("email")
        password = req_body.get("password")
        name = req_body.get("username")
        diet_type = "Test_diet_type"  # req_body.get("diet_type")
        daily_budget = 100  # req_body.get("daily_budget")
        logging.info(f"new_user: {new_user}")
        input_valid, validation_message = register_utils.validate_input(
            email, password, name, diet_type, daily_budget
        )

        if not input_valid:
            return func.HttpResponse(
                json.dumps({"message": validation_message}), status_code=400
            )

        if register_utils.check_user_exists(email):
            return func.HttpResponse(
                json.dumps({"message": "User already exists"}), status_code=409
            )

        new_user.password = register_utils.hash_password(new_user.password)
        # Save the user to the database
        if register_utils.save_user_to_db(new_user):
            return func.HttpResponse(
                json.dumps({"message": "User registration successful"}), status_code=201
            )
        else:
            return func.HttpResponse(
                json.dumps({"message": "An error occurred while registering the user"}),
                status_code=500,
            )

    except ValueError as e:
        # If the JSON is malformed, return a 400 status code
        logging.error(e)
        return func.HttpResponse(
            json.dumps({"message": "Invalid JSON Body"}), status_code=400
        )

    except Exception as e:
        # For any other errors, return a 500 status code
        logging.error(e)
        return func.HttpResponse(
            json.dumps({"message": "An error occurred while registering the user"}),
            status_code=500,
        )
