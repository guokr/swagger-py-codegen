# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

from functools import wraps
from werkzeug.datastructures import MultiDict
from flask import request, g, json
from flask_restful import abort

from . import schemas

validators = {
{%- for key, schema in validators.iteritems() %}
    {{ key }}: schemas.{{ schema }},
{%- endfor %}
}


def request_validate(view):
    @wraps(view)
    def wapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
        for loc in ['headers', 'args', 'form', 'json']:
            s = validators.get((endpoint, request.method, loc), None)
            if not s:
                continue
            value = getattr(request, loc, MultiDict())
            if callable(value):
                value = value()
            # TODO: marshmallow doesn't support MultiDict by default
            result, errors = s().load(value or {})
            if errors:
                abort(422, message='Unprocessable Entity', errors=errors)
            setattr(g, loc, result)
        return view(*args, **kwargs)
    return wapper
