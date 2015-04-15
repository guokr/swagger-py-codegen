# -*- coding: utf-8 -*-
from flask import Flask, Blueprint
import flask_restful as restful

from .validators import request_validate
from .filters import response_filter
from .routes import routes

bp = Blueprint('{{ model.blueprint }}', __name__)
api = restful.Api(bp, catch_all_404s=True)

for route in routes:
    api.add_resource(route.pop('resource'), *route.pop('urls'), **route)

class Resource(restful.Resource):
    method_decorators = [request_validate, response_filter]
