# -*- coding: utf-8 -*-
from flask import request, g
import datetime

from . import Resource
from .. import schemas


class OauthAuthApproach(Resource):

    def post(self):
        print g.headers
        print g.json

        return None

    def get(self):
        print g.headers

        return {'approach': 'poooo', 'identity': 'poooo'}