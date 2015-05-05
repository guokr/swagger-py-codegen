# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from .api.oauth_auth_approach_approach import OauthAuthApproachApproach
from .api.oauth_auth_approach import OauthAuthApproach
from .api.users_current import UsersCurrent
from .api.oauth_token import OauthToken
from .api.users import Users
from .api._swagger import Swagger


routes = [
    {'endpoint': 'oauth_auth_approach_approach', 'resource': OauthAuthApproachApproach, 'urls': ['/oauth/auth_approach/<approach>']},
    {'endpoint': 'oauth_auth_approach', 'resource': OauthAuthApproach, 'urls': ['/oauth/auth_approach']},
    {'endpoint': 'users_current', 'resource': UsersCurrent, 'urls': ['/users/current']},
    {'endpoint': 'oauth_token', 'resource': OauthToken, 'urls': ['/oauth/token']},
    {'endpoint': 'users', 'resource': Users, 'urls': ['/users']},
    {'endpoint': '_swagger', 'resource': Swagger, 'urls': ['/_swagger']},
]