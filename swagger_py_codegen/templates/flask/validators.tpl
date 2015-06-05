# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

from functools import wraps
from werkzeug.datastructures import MultiDict, Headers

from flask import request, g, json, Response
from flask_restful import abort
from flask_restful.utils import unpack
from jsonschema import Draft4Validator

from .schemas import (
    validators, filters, scopes, security, merge_default, object_to_dict)


def _to_dict(obj, location, schema):
    if location == 'json':
        return obj
    if obj is None:
        return obj
    if isinstance(obj, Headers):
        obj = MultiDict(obj.iteritems())
    result = {}
    for k, v in obj.iterlists():
        type_ = schema['properties'].get(k, {}).get('type')
        if type_ == 'array':
            result[k] = v
        else:
            result[k] = v[0]
    return result


def request_validate(view):

    @wraps(view)
    def wrapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
        # scope
        if (endpoint, request.method) in scopes and not set(
                scopes[(endpoint, request.method)]).issubset(set(security.scopes)):
            abort(403)
        # data
        locations = validators.get((endpoint, request.method), {})
        for location, schema in locations.iteritems():
            value = getattr(request, location, MultiDict())
            value = _to_dict(value, location, schema)
            validator = Draft4Validator(schema)
            errors = list(e.message for e in validator.iter_errors(value))
            if errors:
                abort(422, message='Unprocessable Entity', errors=errors)
            result = merge_default(schema, value)
            setattr(g, location, result)
        return view(*args, **kwargs)

    return wrapper


def response_filter(view):

    @wraps(view)
    def wrapper(*args, **kwargs):
        resp = view(*args, **kwargs)

        endpoint = request.endpoint.partition('.')[-1]
        filter = filters.get((endpoint, request.method), None)
        if not filter:
            return resp
        if isinstance(resp, Response):
            return resp

        headers = None
        code = None
        if isinstance(resp, tuple):
            resp, code, headers = unpack(resp)

        if len(filter) == 1:
            code = filter.keys()[0]

        schemas = filter.get(code)
        if not schemas:
            # return resp, code, headers
            abort(500, message='`%d` is not a defined status code.' % code)

        headers, errs_a = object_to_dict(schemas['headers'], headers)
        resp, errs_b = object_to_dict(schemas['schema'], resp)
        errors = errs_a + errs_b
        if errors:
            abort(500, message='Expectation Failed', errors=errors)

        return resp, code, headers

    return wrapper
