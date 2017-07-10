# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
###
### The code is auto generated, your change will be overwritten by
### code generating.
###
from __future__ import absolute_import, print_function

import json
import inspect
from datetime import date
from functools import wraps

import six
from sanic.exceptions import ServerError

from werkzeug.datastructures import MultiDict, Headers
from jsonschema import Draft4Validator

from .schemas import (
    validators, filters, scopes, security, base_path, normalize)


def _remove_characters(text, deletechars):
    return text.translate({ord(x): None for x in deletechars})


def _path_to_endpoint(path):
    endpoint = path.strip('/').replace('/', '_').replace('-', '_')
    _base_path = base_path.strip('/').replace('/', '_').replace('-', '_')
    if endpoint.startswith(_base_path):
        endpoint = endpoint[len(_base_path)+1:]
    return _remove_characters(endpoint, '{}')


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class SanicValidatorAdaptor(object):

    def __init__(self, schema):
        self.validator = Draft4Validator(schema)

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
            obj = MultiDict(obj.items())
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
            fun = convert_funs.get(type_, lambda v: v[0])
            if type_ == 'array':
                item_type = prop.get('items', {}).get('type')
                result[k] = convert_array(item_type, values)
            else:
                result[k] = fun(values)
        return result

    def validate(self, value):
        value = self.type_convert(value)
        print(value)
        print(self.validator.iter_errors(value))
        for e in self.validator.iter_errors(value):
            print(e.path, e.message)
        errors = list(e.message for e in self.validator.iter_errors(value))
        return normalize(self.validator.schema, value)[0], errors


def request_validate(view):

    @wraps(view)
    def wrapper(*args, **kwargs):
        request = args[1]
        endpoint = _path_to_endpoint(request.uri_template)
        # scope
        if (endpoint, request.method) in scopes and not set(
                scopes[(endpoint, request.method)]).issubset(set(security.scopes)):
            raise ServerError('403', status_code=403)
        # data
        method = request.method
        if method == 'HEAD':
            method = 'GET'
        locations = validators.get((endpoint, method), {})
        for location, schema in locations.items():
            print(location)
            value = getattr(request, location, MultiDict())
            if value is None:
                value = MultiDict()
            print(value)
            validator = SanicValidatorAdaptor(schema)
            result, errors = validator.validate(value)
            if errors:
                raise ServerError('Unprocessable Entity', status_code=422)
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

        resp, errors = normalize(schemas['schema'], resp)
        if schemas['headers']:
            headers, header_errors = normalize(
                {'properties': schemas['headers']}, headers)
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