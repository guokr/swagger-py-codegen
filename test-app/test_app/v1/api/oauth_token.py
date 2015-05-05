# -*- coding: utf-8 -*-
from flask import request, g
import datetime

from . import Resource
from .. import schemas


class OauthToken(Resource):

    def post(self):
        print g.json

        return {'access_token': 'poooo', 'token_type': 'Bearer', 'expires_in': 9263, 'scope': ['register']}