# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sanic import Blueprint

from .routes import routes
from .validators import security


@security.scopes_loader
def current_scopes(request):
    return {{ scopes_supported }}

bp = Blueprint('{{ blueprint }}', __name__)

for route in routes:
    route.pop('endpoint', None)
    bp.add_route(route.pop('resource'), *route.pop('urls'), **route)
