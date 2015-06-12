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


class FlaskValidatorAdaptor(object):

    def __init__(self, schema):
        self.validator = Draft4Validator(schema)

    def type_convert(self, obj):
        if obj is None:
            return None
        if isinstance(obj, dict) and not isinstance(obj, MultiDict):
            return obj
        if isinstance(obj, Headers):
            obj = MultiDict(obj.iteritems())
        result = dict()
        convert_funs = {
            'integer': lambda v: int(v[0]),
            'boolean': lambda v: v[0].lower() not in ['n', 'no', 'false', '', '0'],
            'null': lambda v: None,
            'number': lambda v: float(v[0]),
            'array': lambda v: v,
            'string': lambda v: v[0]
        }
        for k, values in obj.iterlists():
            type_ = self.validator.schema['properties'].get(k, {}).get('type')
            fun = convert_funs.get(type_, lambda v: v[0])
            result[k] = fun(values)
        return result

    def validate(self, value):
        value = self.type_convert(value)
        errors = list(e.message for e in self.validator.iter_errors(value))
        return merge_default(self.validator.schema, value), errors


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
            validator = FlaskValidatorAdaptor(schema)
            result, errors = validator.validate(value)
            if errors:
                abort(422, message='Unprocessable Entity', errors=errors)
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
