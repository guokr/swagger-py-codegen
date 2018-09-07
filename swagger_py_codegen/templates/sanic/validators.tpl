# -*- coding: utf-8 -*-
{% include '_do_not_change.tpl' %}
from __future__ import absolute_import, print_function

import re
import json
from datetime import date
from functools import wraps

import six
from sanic import response
from sanic.exceptions import ServerError
from sanic.response import HTTPResponse

from werkzeug.datastructures import MultiDict, Headers
from sanic.request import RequestParameters
from jsonschema import Draft4Validator

from .schemas import (
    validators, filters, scopes, security, resolver, base_path, normalize, current)


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


def _remove_characters(text, deletechars):
    return text.translate({ord(x): None for x in deletechars})


def _path_to_endpoint(path):
    endpoint = '_'.join(filter(None, re.sub(r'(/|<|>|-)', r'_', path).split('_')))
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
        self.validator = Draft4Validator(schema, resolver=resolver)

    def validate_number(self, type_, value):
        try:
            return type_(value)
        except ValueError:
            return value

    def type_convert(self, obj):
        if obj is None:
            return None
        if isinstance(obj, (dict, list)) and not isinstance(obj, RequestParameters):
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

        for k, values in obj.items():
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
        errors = list(e.message for e in self.validator.iter_errors(value))
        return normalize(self.validator.schema, value, resolver=resolver)[0], errors


def request_validate(view):

    @wraps(view)
    def wrapper(*args, **kwargs):
        request = args[1]
        endpoint = _path_to_endpoint(request.uri_template)
        current.request = request
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
            value = getattr(request, location, MultiDict())
            if value is None:
                value = MultiDict()
            validator = SanicValidatorAdaptor(schema)
            result, errors = validator.validate(value)
            if errors:
                raise ServerError('Unprocessable Entity', status_code=422)
        return view(*args, **kwargs)

    return wrapper


def response_filter(view):

    @wraps(view)
    async def wrapper(*args, **kwargs):
        request = args[1]
        resp = view(*args, **kwargs)

        from inspect import isawaitable
        if isawaitable(resp):
            resp = await resp
        if isinstance(resp, HTTPResponse):
            return resp

        endpoint = _path_to_endpoint(request.uri_template)
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
            raise ServerError('`%d` is not a defined status code.' % status, 500)

        resp, errors = normalize(schemas['schema'], resp, resolver=resolver)
        if schemas['headers']:
            headers, header_errors = normalize(
                {'properties': schemas['headers']}, headers, resolver=resolver)
            errors.extend(header_errors)
        if errors:
            raise ServerError('Expectation Failed', 500)

        return response.json(
            resp,
            status=status,
            headers=headers,
        )

    return wrapper
