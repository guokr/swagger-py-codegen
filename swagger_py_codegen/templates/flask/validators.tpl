# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}
from __future__ import absolute_import

from datetime import date
from functools import wraps

import six

from werkzeug.datastructures import MultiDict, Headers
from flask import request, g, current_app, json
from flask_restful import abort
from flask_restful.utils import unpack
from jsonschema import Draft4Validator

from .schemas import (
    validators, filters, scopes, resolver, security, merge_default, normalize)


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class FlaskValidatorAdaptor(object):

    def __init__(self, schema):
        self.validator = Draft4Validator(schema, resolver=resolver)

    def validate_number(self, type_, value):
        try:
            return type_(value)
        except ValueError:
            return value

    def type_convert(self, obj):
        if obj is None:
            return None
        if isinstance(obj, (dict, list)) and not isinstance(obj, MultiDict):
            return obj
        if isinstance(obj, Headers):
            obj = MultiDict(six.iteritems(obj))
        result = dict()

        convert_funs = {
            'integer': lambda v: self.validate_number(int, v[0]),
            'boolean': lambda v: v[0].lower() not in ['n', 'no', 'false', '', '0'],
            'null': lambda v: None,
            'number': lambda v: self.validate_number(float, v[0]),
            'string': lambda v: v[0]
        }

        def convert_array(type_, v):
            func = convert_funs.get(type_, lambda v: v[0])
            return [func([i]) for i in v]

        for k, values in obj.lists():
            prop = self.validator.schema['properties'].get(k, {})
            type_ = prop.get('type')
            if type_ is None and '$ref' in prop:
                ref = prop.get('$ref')
                if not ref:
                    continue
                type_ = self.validator.resolver.resolve(prop.get('$ref'))[1].get('type')
                if not type_:
                    continue
            fun = convert_funs.get(type_, lambda v: v[0])
            if type_ == 'array':
                item_type = prop.get('items', {}).get('type')
                result[k] = convert_array(item_type, values)
            else:
                result[k] = fun(values)
        return result

    def validate(self, value):
        value = self.type_convert(value)
        errors = list(e.message for e in self.validator.iter_errors(value))
        return normalize(self.validator.schema, value, resolver=resolver)[0], errors


def request_validate(view):

    @wraps(view)
    def wrapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
        # scope
        if (endpoint, request.method) in scopes and not set(
                scopes[(endpoint, request.method)]).issubset(set(security.scopes)):
            abort(403)
        # data
        method = request.method
        if method == 'HEAD':
            method = 'GET'
        locations = validators.get((endpoint, method), {})
        for location, schema in six.iteritems(locations):
            value = getattr(request, location, MultiDict())
            if value is None:
                value = MultiDict()
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

        if isinstance(resp, current_app.response_class):
            return resp

        endpoint = request.endpoint.partition('.')[-1]
        method = request.method
        if method == 'HEAD':
            method = 'GET'
        filter = filters.get((endpoint, method), None)
        if not filter:
            return resp

        headers = None
        status = None
        if isinstance(resp, tuple):
            resp, status, headers = unpack(resp)

        if len(filter) == 1:
            if six.PY3:
                status = list(filter.keys())[0]
            else:
                status = filter.keys()[0]

        schemas = filter.get(status)
        if not schemas:
            # return resp, status, headers
            abort(500, message='`%d` is not a defined status code.' % status)

        resp, errors = normalize(schemas['schema'], resp, resolver=resolver)
        if schemas['headers']:
            headers, header_errors = normalize(
                {'properties': schemas['headers']}, headers, resolver=resolver)
            errors.extend(header_errors)
        if errors:
            abort(500, message='Expectation Failed', errors=errors)

        return current_app.response_class(
            json.dumps(resp, cls=JSONEncoder) + '\n',
            status=status,
            headers=headers,
            mimetype='application/json'
        )

    return wrapper
