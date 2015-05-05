# -*- coding: utf-8 -*-
from flask import request, g
import datetime

from . import Resource
from .. import schemas


class UsersCurrent(Resource):

    def get(self):
        print g.headers

        return {'nickname': 'poooo', 'avatar': 'poooo'}