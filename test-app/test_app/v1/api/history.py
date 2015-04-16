# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class History(Resource):

    def get(self):
        print g.args

        return {'count': 9263, 'offset': 9263, 'limit': 9263, 'history': 'nullll'}, 200