# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from functools import wraps
from werkzeug.datastructures import MultiDict
from flask import request, g, json
from flask_restful import abort

from . import schemas

validators = {
    ('history', 'GET', 'args'): (schemas.HistoryGETArgsSchema, False),
    ('products', 'GET', 'args'): (schemas.ProductsGETArgsSchema, False),
    ('estimates_price', 'GET', 'args'): (schemas.EstimatesPriceGETArgsSchema, False),
    ('estimates_time', 'GET', 'args'): (schemas.EstimatesTimeGETArgsSchema, False),
}


def request_validate(view):
    @wraps(view)
    def wapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
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
    return wapper