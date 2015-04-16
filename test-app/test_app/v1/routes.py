# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

from .api.products import Products
from .api.estimates import EstimatesPrice
from .api.estimates import EstimatesTime
from .api.history import History
from .api.me import Me


routes = [
    {'endpoint': 'products', 'resource': Products, 'urls': ['/products']},
    {'endpoint': 'estimates_price', 'resource': EstimatesPrice, 'urls': ['/estimates/price']},
    {'endpoint': 'estimates_time', 'resource': EstimatesTime, 'urls': ['/estimates/time']},
    {'endpoint': 'history', 'resource': History, 'urls': ['/history']},
    {'endpoint': 'me', 'resource': Me, 'urls': ['/me']},
]