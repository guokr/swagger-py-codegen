# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from functools import wraps
from werkzeug.datastructures import MultiDict
from flask import request, g, json
from flask_restful import abort

from . import schemas

validators = {
    ('users_current', 'GET', 'headers'): (schemas.UsersCurrentGETHeadersSchema, False),
    ('oauth_auth_approach', 'POST', 'json'): (schemas.ApproachSchema, False),
    ('oauth_token', 'POST', 'json'): (schemas.AuthenticationSchema, False),
    ('users', 'POST', 'headers'): (schemas.UsersPOSTHeadersSchema, False),
    ('oauth_auth_approach', 'POST', 'headers'): (schemas.OauthAuthApproachPOSTHeadersSchema, False),
    ('oauth_auth_approach', 'GET', 'headers'): (schemas.OauthAuthApproachGETHeadersSchema, False),
    ('users', 'POST', 'json'): (schemas.UserSchema, False),
    ('oauth_auth_approach_approach', 'GET', 'headers'): (schemas.OauthAuthApproachApproachGETHeadersSchema, False),
    ('oauth_auth_approach_approach', 'DELETE', 'headers'): (schemas.OauthAuthApproachApproachDELETEHeadersSchema, False),
}

scopes = {
    ('oauth_auth_approach', 'GET'): ['open'],
    ('oauth_auth_approach_approach', 'GET'): ['open'],
    ('users_current', 'GET'): ['open'],
    ('users', 'POST'): ['register'],
    ('oauth_auth_approach_approach', 'DELETE'): ['open'],
    ('oauth_auth_approach', 'POST'): ['open'],
}


class Security(object):

    def __init__(self):
        super(Security, self).__init__()
        self._loader = lambda: []

    @property
    def scopes(self):
        return self._loader()

    def scopes_loader(self, func):
        self._loader = func
        return func

security = Security()


def request_validate(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
        # scope
        if (endpoint, request.method) in scopes and not set(
                scopes[(endpoint, request.method)]).issubset(set(security.scopes)):
            abort(403)
        # data
        for loc in ['headers', 'args', 'form', 'json']:
            v = validators.get((endpoint, request.method, loc), None)
            if not v:
                continue
            value = getattr(request, loc, MultiDict())
            if callable(value):
                value = value()
            # TODO: marshmallow doesn't support MultiDict by default
            result, errors = v[0](many=v[1]).load(value or {})
            if errors:
                abort(422, message='Unprocessable Entity', errors=errors)
            setattr(g, loc, result)
        return view(*args, **kwargs)
    return wrapper