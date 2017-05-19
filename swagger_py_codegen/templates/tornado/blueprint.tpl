# -*- coding: utf-8 -*-
from __future__ import absolute_import

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
        return {{ scopes_supported }}

    @property
    def account(self):
        if self._account is None:
            if self.valid and self.user_id:
                # TODO: test
                self._account = None
        return self._account