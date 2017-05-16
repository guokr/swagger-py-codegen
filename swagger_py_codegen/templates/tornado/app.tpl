# -*- coding: utf-8 -*-

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

def main():
    import socket
    socket.setdefaulttimeout(2)
    url_list = []
    url_list.extend(config.URIS)

    app_settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
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
