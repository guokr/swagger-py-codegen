# -*- coding: utf-8 -*-
from __future__ import absolute_import

import falcon
from wsgiref import simple_server

import {{ blueprint }}


def create_app():
    app = falcon.API()
    register_routes(app)
    return app


def register_routes(app):
    for route in {{ blueprint }}.routes:
        app.add_route(route.pop('url'), route.pop('resource'))


if __name__ == '__main__':
    app = create_app()
    httpd = simple_server.make_server('127.0.0.1', 8888, app)
    httpd.serve_forever()
