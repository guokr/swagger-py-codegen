# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}
from __future__ import absolute_import
import tornado.web
from tornado.httputil import HTTPHeaders
from werkzeug.datastructures import MultiDict

import json
import six
from functools import wraps
from jsonschema import Draft4Validator

from .schemas import validators, scopes, resolver, normalize, filters


class ValidatorAdaptor(object):

    def __init__(self, schema):
        self.validator = Draft4Validator(schema, resolver=resolver)

    def validate_number(self, type_, value):
        try:
            return type_(value)
        except ValueError:
            return value

    def type_convert(self, obj):
        if obj is None or not obj:
            return None
        if six.PY3:
            if isinstance(obj, str):
                obj = MultiDict(json.loads(obj))
        else:
            if isinstance(obj, (str, unicode, basestring)):
                obj = MultiDict(json.loads(obj))
        if isinstance(obj, (dict, list)) and not isinstance(obj, MultiDict):
            return obj
        if isinstance(obj, HTTPHeaders):
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

def request_validate(obj):
    def _request_validate(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            request = obj.request
            endpoint = obj.endpoint
            user_info = obj.current_user
            if (endpoint, request.method) in scopes and not set(
                    scopes[(endpoint, request.method)]
            ).issubset(set(user_info.scopes)):
                raise tornado.web.HTTPError(403)

            method = request.method
            if method == 'HEAD':
                method = 'GET'
            locations = validators.get((endpoint, method), {})
            for location, schema in six.iteritems(locations):
                if location == 'json':
                    value = getattr(request, 'body', MultiDict())
                elif location == 'args':
                    value = getattr(request, 'query_arguments', MultiDict())
                    for k,v in six.iteritems(value):
                        if isinstance(v, list) and len(v) == 1:
                            value[k] = v[0]
                    value = MultiDict(value)
                else:
                    value = getattr(request, location, MultiDict())
                validator = ValidatorAdaptor(schema)
                result, reasons = validator.validate(value)
                if reasons:
                    raise tornado.web.HTTPError(422, message='Unprocessable Entity',
                                                reason=json.dumps(reasons))
                setattr(obj, location, result)
            return view(*args, **kwargs)
        return wrapper
    return _request_validate


def response_filter(obj):
    def _response_filter(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            resp = view(*args, **kwargs)
            request = obj.request
            endpoint = obj.endpoint
            method = request.method
            if method == 'HEAD':
                method = 'GET'
            headers = None
            status = None
            if isinstance(resp, tuple):
                resp, status, headers = unpack(resp)
            filter = filters.get((endpoint, method), None)
            if filter:
                if len(filter) == 1:
                    if six.PY3:
                        status = list(filter.keys())[0]
                    else:
                        status = filter.keys()[0]

                schemas = filter.get(status)
                if not schemas:
                    # return resp, status, headers
                    raise tornado.web.HTTPError(
                        500, message='`%d` is not a defined status code.' % status)

                resp, errors = normalize(schemas['schema'], resp, resolver=resolver)
                if schemas['headers']:
                    headers, header_errors = normalize(
                        {'properties': schemas['headers']}, headers, resolver=resolver)
                    errors.extend(header_errors)
                if errors:
                    raise tornado.web.HTTPError(
                        500, message='Expectation Failed',
                        reason=json.dumps(errors))
            obj.set_status(status)
            obj.set_headers(headers)
            obj.write(json.dumps(resp))
            return
        return wrapper
    return _response_filter


def unpack(value):
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
