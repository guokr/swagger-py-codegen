# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from functools import wraps
from flask import request, Response
from flask_restful.utils import unpack

from . import schemas

filters = {
    ('products', 'GET'): (
        schemas.ProductSchema,
        200,
        True),
    ('estimates_time', 'GET'): (
        schemas.ProductSchema,
        200,
        True),
    ('history', 'GET'): (
        schemas.ActivitiesSchema,
        200,
        False),
    ('estimates_price', 'GET'): (
        schemas.PriceEstimateSchema,
        200,
        True),
    ('me', 'GET'): (
        schemas.ProfileSchema,
        200,
        False),
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