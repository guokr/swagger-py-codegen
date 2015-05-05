# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from marshmallow import Schema, fields, validate


class OauthAuthApproachGETHeadersSchema(Schema):
     access_token = fields.String(required=True)


class OauthAuthApproachApproachGETHeadersSchema(Schema):
     access_token = fields.String(required=True)


class UsersCurrentGETHeadersSchema(Schema):
     access_token = fields.String(required=True)


class AuthenticationSchema(Schema):
     username = fields.String(required=True)
     grant_type = fields.Enum(choices=['password', 'refresh_token'])
     auth_approach = fields.Enum(choices=['weibo', 'weixin', 'email', 'phone'])
     client_id = fields.String(required=True)
     client_secret = fields.String(required=True)
     password = fields.String(required=True)


class UsersPOSTHeadersSchema(Schema):
     access_token = fields.String(required=True)


class TokenSchema(Schema):
     access_token = fields.String()
     token_type = fields.String(default='Bearer')
     expires_in = fields.Integer()
     scope = fields.List(cls_or_instance=fields.Enum(choices=['register', 'open']))


class UserSchema(Schema):
     nickname = fields.String()
     avatar = fields.String()


class ErrorSchema(Schema):
     message = fields.String()
     code = fields.Integer()
     fields_ = fields.String()


class OauthAuthApproachPOSTHeadersSchema(Schema):
     access_token = fields.String(required=True)


class ApproachSchema(Schema):
     approach = fields.String()
     identity = fields.String()


class OauthAuthApproachApproachDELETEHeadersSchema(Schema):
     access_token = fields.String(required=True)
