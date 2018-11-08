# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import falcon

from .routes import routes
from .validators import security, current


@security.scopes_loader
def current_scopes():
    return {{ scopes_supported }}
