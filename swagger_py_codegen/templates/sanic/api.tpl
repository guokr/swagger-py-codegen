# -*- coding: utf-8 -*-
from __future__ import absolute_import

import inspect

from sanic.views import HTTPMethodView

from ..validators import request_validate, response_filter

before_decorators = [request_validate]
after_decorators = [response_filter]

methods = ['get', 'put', 'post', 'delete']


def add_before_decorators(model_class):
    for name, m in inspect.getmembers(model_class, inspect.isfunction):
        if name in methods:
            for dec in before_decorators:
                m = dec(m)
            setattr(model_class, name, m)


def add_after_decorators(model_class):
    for name, m in inspect.getmembers(model_class, inspect.isfunction):
        if name in methods:
            for dec in after_decorators:
                m = dec(m)
            setattr(model_class, name, m)


class APIMetaclass(type):
    """
    Metaclass of the Model.
    """
    def __init__(cls, name, bases, attrs):
        super(APIMetaclass, cls).__init__(name, bases, attrs)
        add_before_decorators(cls)
        add_after_decorators(cls)


class Resource(HTTPMethodView, metaclass=APIMetaclass):


    pass
