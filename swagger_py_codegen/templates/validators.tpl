# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

from functools import wraps
from werkzeug.datastructures import MultiDict
from flask import request, g, json
from flask_restful import abort

from . import schemas

validators = {
{%- for key, validator in validators.iteritems() %}
    {{ key }}: (schemas.{{ validator.schema }}, {{ validator.many }}),
{%- endfor %}
}

scopes = {
{%- for key, scope in scopes.iteritems() %}
    {{ key }}: {{ scope }},
{%- endfor %}
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
