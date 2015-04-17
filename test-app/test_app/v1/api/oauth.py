# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class OauthAuthApproachApproach(Resource):

    def delete(self, approach):
        print g.headers

    def get(self, approach):
        print g.headers

        return {'approach': 'poooo', 'identity': 'poooo'}, 200


class OauthAuthApproach(Resource):

    def post(self):
        print g.headers
        print g.json

    def get(self):
        print g.headers

        return {'approach': 'poooo', 'identity': 'poooo'}, 200


class OauthToken(Resource):

    def post(self):
        print g.json

        return {'access_token': 'poooo', 'token_type': 'Bearer', 'expires_in': 9263, 'scope': ['register']}, 201