# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import falcon

from ..validators import  request_validate, response_filter

import inspect

before_decorators = [request_validate]
after_decorators = [response_filter]


def add_before_decorators(model_class):
    for name, m in inspect.getmembers(model_class, inspect.ismethod):
        if name in ['on_get', 'on_post', 'on_put', 'on_delete']:
            setattr(model_class, name, falcon.before(*before_decorators)(m))


def add_after_decorators(model_class):
    for name, m in inspect.getmembers(model_class, inspect.ismethod):
        if name in ['on_get', 'on_post', 'on_put', 'on_delete']:
            setattr(model_class, name, falcon.after(*after_decorators)(m))


class APIMetaclass(type):

    """
    Metaclass of the Model.
    """

    def __init__(cls, name, bases, attrs):
        super(APIMetaclass, cls).__init__(name, bases, attrs)
        add_before_decorators(cls)
        add_after_decorators(cls)
