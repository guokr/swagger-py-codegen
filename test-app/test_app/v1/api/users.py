# -*- coding: utf-8 -*-
from flask import request, g
import datetime

from . import Resource
from .. import schemas


class Users(Resource):

    def post(self):
        print g.headers
        print g.json

        return None