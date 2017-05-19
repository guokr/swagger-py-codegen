# -*- coding: utf-8 -*-
from __future__ import absolute_import

from core import RequestHandler
from .. import UserInfo
from ..validators import request_validate, response_filter

class ApiHandler(RequestHandler):
    on_initialize_decorators = [response_filter, request_validate]

    def get_current_user(self):
        authorization = self.request.headers.get('Authorization', '')
        user_id = self.request.headers.get('user_id')

        return UserInfo(user_id, authorization, self.blueprint)