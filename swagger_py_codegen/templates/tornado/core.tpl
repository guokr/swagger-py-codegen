# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import importlib
import tornado.web

settings = {}

def load_tornado_settings(*modules):
    settings.update({'MODULES': modules})
    kwargs = {}
    mods = []
    config = Config()

    for module in modules:
        try:
            mods.append(importlib.import_module('%s.settings' % module))
        except ImportError, err:
            raise ImportError(
                "Could not import settings '%s' (Is it on sys.path?): %s" % (
                    module, err))

    for module in modules:
        try:
            mods.append(importlib.import_module('%s.my_settings' % module))
        except ImportError:
            pass

    for mod in mods:
        if hasattr(mod, 'load_settings'):
            getattr(mod, 'load_settings')(config, **kwargs)

    return config

class RequestHandler(tornado.web.RequestHandler):
    on_initialize_decorators = []

    def initialize(self):
        request = self.request
        meth = getattr(self, self.request.method.lower(), None)
        if meth is None and self.request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        for decorator in self.on_initialize_decorators:
            meth = decorator(meth)

        setattr(self, self.request.method.lower(), meth)

    def set_headers(self, items):
        if items is None:
            return
        for k, v in items:
            self.set_header(k, v)

class Config(object):
    def __getitem__(self, item):
        return getattr(self, item)

    def update(self, **kw):
        for name, value in kw.items():
            self.__setattr__(name, value)

    def setdefault(self, key, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            setattr(self, key, default)
        return default

    def uri_tuple(self, route, url_prefix):
        route['resource'].endpoint = route['endpoint']
        route['resource'].blueprint = url_prefix.replace('/', '_')
        if url_prefix:
            return r'/' + url_prefix + route['urls'][0], route['resource']
        return route['urls'][0], route['resource']

    def update_uri(self, routes, url_prefix=r''):
        self.ROUTES.extend(routes)
        self.URIS.extend([self.uri_tuple(r, url_prefix) for r in routes])

    URIS = []
    ROUTES = []