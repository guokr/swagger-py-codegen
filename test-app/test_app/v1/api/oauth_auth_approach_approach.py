# -*- coding: utf-8 -*-
from flask import request, g
import datetime

from . import Resource
from .. import schemas


class OauthAuthApproachApproach(Resource):

    def delete(self, approach):
        print g.headers

        return None

    def get(self, approach):
        print g.headers

        return {'approach': 'poooo', 'identity': 'poooo'}