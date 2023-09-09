import logging
import json
import azure.functions as func
import utils.register_utils as login_utils

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        email = req_body.get('email')
        password = req_body.get('password')
        if not email or not password:
            return func.HttpResponse(json.dumps({"message": "Invalid JSON Body"}), status_code=400)
        user_authenticated, message = login_utils.authenticate_user(email, password)
        if user_authenticated:
            return func.HttpResponse(json.dumps({"message": "User authenticated"}), status_code=200)
        else:
            return func.HttpResponse(json.dumps({"message": message}), status_code=401)
    except ValueError as e:
        return func.HttpResponse(json.dumps({"message": e}), status_code=400)
    
