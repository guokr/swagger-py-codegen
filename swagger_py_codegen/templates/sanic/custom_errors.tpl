# -*- coding: utf-8 -*-
{% include '_do_not_change.tpl' %}

from sanic.exceptions import SanicException

def add_status_code(code):
    """
    Decorator used for adding exceptions to _sanic_exceptions.
    """
    def class_decorator(cls):
        cls.status_code = code
        return cls
    return class_decorator


class JSONException(SanicException):

    def __init__(self, code, message=None, errors=None, status_code=None):
        super().__init__(message)
        self.error_code = code
        self.message = message
        self.errors = errors

        if status_code is not None:
            self.status_code = status_code


@add_status_code(422)
class UnprocessableEntity(JSONException):
    pass

@add_status_code(401)
class Unauthorized(JSONException):
    pass


@add_status_code(403)
class Forbidden(JSONException):
    pass


@add_status_code(500)
class ServerError(JSONException):
    pass