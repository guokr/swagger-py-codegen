# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

url_prefix = '{{ blueprint }}'

settings = {}


def load_settings(config):
    config.update(**settings)
    try:
        from .routes import routes
        config.update_uri(routes, url_prefix)
    except:
        pass