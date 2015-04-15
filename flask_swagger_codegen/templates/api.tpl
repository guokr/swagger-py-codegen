# -*- coding: utf-8 -*-
import flask_restful as restful

from ..validators import request_validate
from ..filters import response_filter


class Resource(restful.Resource):
    method_decorators = [request_validate, response_filter]
