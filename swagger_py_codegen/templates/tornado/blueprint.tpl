# -*- coding: utf-8 -*-
from __future__ import absolute_import
from services.verification import verify_request

from model.user import User

class UserInfo(object):
    _scopes = None
    client_id = None
    _account = None

    def __init__(self, user_id, authorization, blueprint):
        self.authorization = authorization
        self.user_id = user_id
        self.blueprint = blueprint
        self.valid = False

    @property
    def scopes(self):
        if self._scopes is None:
            self._scopes = self._loader()
        return self._scopes

    def _loader(self):
        valid, token_info = verify_request(self.authorization, self.blueprint)
        self.valid = valid
        if valid and token_info:
            if isinstance(token_info, list):
                scopes = set(token_info) - set(['open'])
                return list(scopes)
            self.client_id = token_info.get('client_id', 'weixin')
            return token_info.get('scopes', [])
        # TODO: test return open, panel
        return ['panel', 'open', 'backend']
        # return []

    @property
    def account(self):
        if self._account is None:
            if self.valid and self.user_id:
                # TODO: test
                self._account = User.query.get(1)
        return self._account


def before_request(obj):
    pass


def after_request(obj):
    pass