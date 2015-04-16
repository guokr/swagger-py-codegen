# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class EstimatesPrice(Resource):

    def get(self):
        print g.args

        return [{'display_name': 'poooo', 'product_id': 'poooo', 'high_estimate': 83.75, 'low_estimate': 83.75, 'surge_multiplier': 83.75, 'estimate': 'poooo', 'currency_code': 'poooo'}], 200


class EstimatesTime(Resource):

    def get(self):
        print g.args

        return [{'display_name': 'poooo', 'image': 'poooo', 'capacity': 'poooo', 'product_id': 'poooo', 'description': 'poooo'}], 200