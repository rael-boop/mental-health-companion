from fastapi import HTTPException


class AppUtils:
    @staticmethod
    def create_response(message=None, data={}):
        return {
            "message": message,
            "data": data
        }


class CustomError(HTTPException):
    pass
