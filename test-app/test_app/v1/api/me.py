# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class Me(Resource):

    def get(self):

        return {'picture': 'poooo', 'first_name': 'poooo', 'last_name': 'poooo', 'email': 'poooo', 'promo_code': 'poooo'}, 200