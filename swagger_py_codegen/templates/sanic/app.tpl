# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import NotFound, InvalidUsage

import {{ blueprint }}


def create_app():
    app = Sanic(__name__)
    app.static('/static', './static')
    app.blueprint({{ blueprint }}.bp)
    return app


app = create_app()

@app.exception(NotFound)
def not_found(request, exception):
    return json({'error_code': 'not_found',
                 'message': exception.args[0]},
                status=exception.status_code,
                )


@app.exception(InvalidUsage)
def method_not_allow(request, exception):
    return json({'error_code': 'method_not_allow',
                 'message': exception.args[0]},
                status=exception.status_code,
                )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
