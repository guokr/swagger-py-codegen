# -*- coding: utf-8 -*-
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from core import load_tornado_settings

modules = ['{{ blueprint }}']
config = load_tornado_settings(*modules)

class Application(tornado.web.Application):
    def __init__(self, url_list, **app_settings):
        tornado.web.Application.__init__(self, url_list, **app_settings)
        self.config = config


class RestfulErrorHandler(tornado.web.ErrorHandler):
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


def main():
    import socket

    socket.setdefaulttimeout(2)
    url_list = []
    url_list.extend(config.URIS)

    app_settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "default_handler_class": RestfulErrorHandler,
        "default_handler_args": dict(status_code=404)

    }

    app = Application(url_list,
                      debug=config.DEBUG,
                      **app_settings)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(config.PORT)
    http_server.start(config.WORKER)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
