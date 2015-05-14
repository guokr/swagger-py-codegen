# -*- coding: utf-8 -*-
from flask import Flask, Blueprint
import flask_restful as restful

from .routes import routes
from .validators import security


@security.scopes_loader
def current_scopes():
    return {{ model.supported_scope_set }}

bp = Blueprint('{{ model.blueprint }}', __name__)
api = restful.Api(bp, catch_all_404s=True)

for route in routes:
    api.add_resource(route.pop('resource'), *route.pop('urls'), **route)
