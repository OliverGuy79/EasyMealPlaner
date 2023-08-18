import logging
import os
import azure.functions as func
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Assuming the function is running at the root of your function app
    file_path = os.path.join(os.getcwd(), "QmlLoader/qml/login.qml")
    logging.info(file_path)
    try:
        with open(file_path, "r") as file:
            content = file.read()
            response = {"qmlCode": content}

        return func.HttpResponse(body=json.dumps(response), status_code=200)

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return func.HttpResponse(f"File not found: {file_path}", status_code=404)
