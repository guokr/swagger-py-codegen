# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from functools import wraps
from flask import request, Response
from flask_restful import abort
from flask_restful.utils import unpack

from . import schemas

filters = {
    ('oauth_auth_approach', 'GET'): (
        schemas.ApproachSchema,
        200,
        False),
    ('users_current', 'GET'): (
        schemas.UserSchema,
        200,
        False),
    ('oauth_auth_approach_approach', 'GET'): (
        schemas.ApproachSchema,
        200,
        False),
    ('oauth_token', 'POST'): (
        schemas.TokenSchema,
        201,
        False),
}


def response_filter(view):
    @wraps(view)
    def wapper(*args, **kwargs):
        resp = view(*args, **kwargs)

        endpoint = request.endpoint.partition('.')[-1]
        filter = filters.get((endpoint, request.method), None)
        if not filter:
            return resp
        if isinstance(resp, Response):
            return resp

        headers = {}
        if isinstance(resp, tuple):
            resp, code, headers = unpack(resp)

        schema = filter[0](many=filter[2])
        code = filter[1]
        data, errors = schema.dump(resp)
        if errors:
            abort(500, message='Expectation Failed', errors=errors)
        return data, code, headers
    return wapper