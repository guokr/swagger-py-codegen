# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class UsersCurrent(Resource):

    def get(self):
        print g.headers

        return {'nickname': 'poooo', 'avatar': 'poooo'}, 200


class Users(Resource):

    def post(self):
        print g.headers
        print g.json