import json

from flask import make_response
from werkzeug.exceptions import HTTPException


class NotFound(HTTPException):
    def __init__(self, status_code, error_message):
        message = {"error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


class Invalid(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)