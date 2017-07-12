# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from six import with_metaclass
import six
import falcon

from ..validators import  request_validate, response_filter

import inspect

before_decorators = [request_validate]
after_decorators = [response_filter]


if six.PY3:
    ismethod = inspect.isfunction
else:
    ismethod = inspect.ismethod


def add_before_decorators(model_class):
    for name, m in inspect.getmembers(model_class, ismethod):
        if name in ['on_get', 'on_post', 'on_put', 'on_delete']:
            setattr(model_class, name, falcon.before(*before_decorators)(m))


def add_after_decorators(model_class):
    for name, m in inspect.getmembers(model_class, ismethod):
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

class Resource(with_metaclass(APIMetaclass, object)):

    pass