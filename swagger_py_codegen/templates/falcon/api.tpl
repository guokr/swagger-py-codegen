# -*- coding: utf-8 -*-
from __future__ import absolute_import

import falcon

from ..validators import  request_validate, response_filter

import inspect

before_decorators = [request_validate]
after_decorators = [response_filter]


class Validators(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, cls):
        for name, m in inspect.getmembers(cls, inspect.ismethod):
            if name in ['on_get', 'on_post', 'on_put', 'on_delete']:
                setattr(cls, name, self.f(m))
        return cls
