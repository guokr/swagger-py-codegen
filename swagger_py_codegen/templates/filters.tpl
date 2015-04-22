# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

from functools import wraps
from flask import request, Response
from flask_restful.utils import unpack

from . import schemas

filters = {
{%- for key, filter in filters.iteritems() %}
    {{ key }}: (
        schemas.{{ filter.schema }},
        {{ filter.code }},
        {{ filter.many }}),
{%- endfor %}
}


def response_filter(view):
    @wraps(view)
    def wapper(*args, **kwargs):
        resp = view(*args, **kwargs)

        endpoint = request.endpoint.partition('.')[-1]
        filter = filters.get((endpoint, request.method), None)
        if not filter:
            return resp
        if isinstance(resp, Response):
            return resp

        headers = {}
        if isinstance(resp, tuple):
            resp, code, headers = unpack(resp)

        schema = filter[0](many=filter[2])
        code = filter[1]
        data, err = schema.dump(resp)
        if err:
            abort(417, message='Expectation Failed', errors=errors)
        return data, code, headers
    return wapper
