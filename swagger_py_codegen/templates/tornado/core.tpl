# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import six
import importlib
import tornado.web

settings = {}

def load_tornado_settings(*modules):
    settings.update({'MODULES': modules})
    kwargs = {}
    mods = []
    config = Config()
    config.update(**settings)
    try:
        setting_mod = importlib.import_module('my_settings')
        if hasattr(setting_mod, 'load_settings'):
            getattr(setting_mod, 'load_uris')(config, **kwargs)
    except ImportError:
        pass

    for module in modules:
        try:
            mods.append(importlib.import_module('%s.routes' % module))
        except ImportError:
            raise ImportError(
                "Could not import routers '%s' (Is it on sys.path?)" % (
                    module))

    for mod in mods:
        if hasattr(mod, 'load_uris'):
            getattr(mod, 'load_uris')(config, **kwargs)

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
            meth = decorator(self)(meth)

        setattr(self, self.request.method.lower(), meth)

    def set_headers(self, items):
        if items is None:
            return
        for k, v in items:
            self.set_header(k, v)

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages.

        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.

        If this error was caused by an uncaught exception (including
        HTTPError), an ``exc_info`` triple will be available as
        ``kwargs["exc_info"]``.  Note that this exception may not be
        the "current" exception for purposes of methods like
        ``sys.exc_info()`` or ``traceback.format_exc``.
        """
        self.finish({
            "code": status_code,
            "message": self._reason,
        })

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
    DEBUG = True
    PORT = 5000
    WORKER = 1
