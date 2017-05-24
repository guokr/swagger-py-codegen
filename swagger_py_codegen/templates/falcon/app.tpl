# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import mimetypes

import falcon
from wsgiref import simple_server

import {{blueprint}}


class NotFoundError(object):

    def process_response(self, req, resp, resource):
        if resp.status.find('404') > -1 and resp.body is None:
            description = ('The requested URL [%s] was not found on the server' % req.path)
            raise falcon.HTTPError(falcon.HTTP_404,
                                   'URL Not Found',
                                   description)


class StaticAdapter(object):

    def __call__(self, req, resp, filename):
        file_path = os.path.join(os.path.dirname(__file__), "static/%s" % filename)
        file_type = mimetypes.guess_type(file_path)[0]
        resp.status = falcon.HTTP_200
        resp.content_type = file_type
        with open(file_path, 'r') as f:
            resp.body = f.read()


def http_error_serializer(req, resp, exception):
    representation = None
    preferred = req.client_prefers(('application/x-yaml',
                                    'application/json'))

    if preferred is not None:
        if preferred == 'application/json':
            representation = exception.to_json()
        else:
            representation = yaml.dump(exception.to_dict(),
                                       encoding=None)
        resp.body = representation
        resp.content_type = preferred

    resp.append_header('Vary', 'Accept')


def create_app():
    app = falcon.API(middleware=[NotFoundError()])
    app.set_error_serializer(http_error_serializer)
    register_routes(app)
    return app


def register_routes(app):
    for route in {{blueprint}}.routes:
        url = '{prefix}{base_url}'.format(prefix='{{base_path}}',
                                          base_url=route.pop('url'))
        app.add_route(url, route.pop('resource'))
    static = StaticAdapter()
    app.add_sink(static, r'/static/(?P<filename>.*)')


if __name__ == '__main__':
    app = create_app()
    httpd = simple_server.make_server('127.0.0.1', 5000, app)
    httpd.serve_forever()
