# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}
from __future__ import absolute_import, print_function

import json
from datetime import date
from functools import wraps

import six
import falcon

from werkzeug.datastructures import MultiDict, Headers
from jsonschema import Draft4Validator

from .schemas import (
    validators, filters, scopes, resolver, security, base_path, normalize)


if six.PY3:
    def _remove_characters(text, deletechars):
        return text.translate({ord(x): None for x in deletechars})
else:
    def _remove_characters(text, deletechars):
        return text.translate(None, deletechars)


def _path_to_endpoint(path):
    endpoint = path.strip('/').replace('/', '_').replace('-', '_')
    _base_path = base_path.strip('/').replace('/', '_').replace('-', '_')
    if endpoint.startswith(_base_path):
        endpoint = endpoint[len(_base_path)+1:]
    return _remove_characters(endpoint, '{}')


class Current(object):

    request = None


current = Current()


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class FalconValidatorAdaptor(object):

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


def request_validate(req, resp, resource, params):

    current.request = req
    endpoint = _path_to_endpoint(req.uri_template)
    # scope
    if (endpoint, req.method) in scopes and not set(
            scopes[(endpoint, req.method)]).issubset(set(security.scopes)):
        raise falcon.HTTPUnauthorized('invalid client')
    # data
    method = req.method
    if method == 'HEAD':
        method = 'GET'
    locations = validators.get((endpoint, method), {})
    context = {}
    for location, schema in six.iteritems(locations):
        value = getattr(req, location, MultiDict())
        if location == 'headers':
            value = {k.capitalize(): v for k, v in value.items()}
        elif location == 'json':
            body = req.stream.read()

            try:
                value = json.loads(body.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                raise falcon.HTTPUnprocessableEntity(
                    'Malformed JSON',
                    'Could not decode the request body. The '
                    'JSON was incorrect or not encoded as '
                    'UTF-8.')
        if value is None:
            value = MultiDict()
        validator = FalconValidatorAdaptor(schema)
        result, errors = validator.validate(value)
        if errors:
            raise falcon.HTTPUnprocessableEntity('Unprocessable Entity', description=errors)
        context[location] = result
    req.context = context


def response_filter(req, resp, resource):

    endpoint = _path_to_endpoint(req.uri_template)
    method = req.method
    if method == 'HEAD':
        method = 'GET'
    filter = filters.get((endpoint, method), None)
    if not filter:
        return resp

    headers = None
    status = None

    if len(filter) == 1:
        if six.PY3:
            status = list(filter.keys())[0]
        else:
            status = filter.keys()[0]

    schemas = filter.get(status)
    if not schemas:
        # return resp, status, headers
        raise falcon.HTTPInternalServerError(
            'Not defined',
            description='`%d` is not a defined status code.' % status)

    _resp, errors = normalize(schemas['schema'], req.context['result'], resolver=resolver)
    if schemas['headers']:
        headers, header_errors = normalize(
            {'properties': schemas['headers']}, headers, resolver=resolver)
        errors.extend(header_errors)
    if errors:
        raise falcon.HTTPInternalServerError(title='Expectation Failed',
                                             description=errors)

    if 'result' not in req.context:
        return
    resp.body = json.dumps(_resp)
