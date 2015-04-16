# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from marshmallow import Schema, fields, validate


class ActivitySchema(Schema):
     uuid = fields.String()


class ProfileSchema(Schema):
     picture = fields.String()
     first_name = fields.String()
     last_name = fields.String()
     email = fields.String()
     promo_code = fields.String()


class ActivitiesSchema(Schema):
     count = fields.Integer()
     history = fields.Nested(nested=ActivitySchema)
     limit = fields.Integer()
     offset = fields.Integer()


class ProductSchema(Schema):
     capacity = fields.String()
     image = fields.String()
     display_name = fields.String()
     product_id = fields.String()
     description = fields.String()


class EstimatesPriceGETArgsSchema(Schema):
     start_longitude = fields.Decimal(required=True)
     end_longitude = fields.Decimal(required=True)
     start_latitude = fields.Decimal(required=True)
     end_latitude = fields.Decimal(required=True)


class HistoryGETArgsSchema(Schema):
     limit = fields.Integer()
     offset = fields.Integer()


class EstimatesTimeGETArgsSchema(Schema):
     start_longitude = fields.Decimal(required=True)
     customer_uuid = fields.UUID()
     start_latitude = fields.Decimal(required=True)
     product_id = fields.String()


class ProductsGETArgsSchema(Schema):
     latitude = fields.Decimal(required=True)
     longitude = fields.Decimal(required=True)


class ErrorSchema(Schema):
     code = fields.Integer()
     message = fields.String()
     _fields = fields.String()


class PriceEstimateSchema(Schema):
     display_name = fields.String()
     product_id = fields.String()
     high_estimate = fields.Float()
     low_estimate = fields.Float()
     surge_multiplier = fields.Float()
     estimate = fields.String()
     currency_code = fields.String()
