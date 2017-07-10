# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sanic import Sanic

import {{ blueprint }}


def create_app():
    app = Sanic(__name__)
    app.register_blueprint(
        {{ blueprint }}.bp,
        url_prefix='{{ base_path }}')
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
