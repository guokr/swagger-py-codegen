# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import falcon

from . import  Validators, before_decorators, after_decorators


@Validators(falcon.before(*before_decorators))
@Validators(falcon.after(*after_decorators))
class {{ name }}(object):

    {%- for method, ins in methods.items() %}

    def on_{{ method.lower() }}(self, req, resp{{ params.__len__() and ', ' or '' }}{{ params | join(', ') }}):
        {%- for request in ins.requests %}
        print(req.options['{{ request }}'])
        {%- endfor %}

        {% if 'response' in  ins -%}
        req.context['result'] = {{ ins.response.0 }}
        resp.status = {{ ins.response.1 }}
        resp.set_headers({{ ins.response.2 }})
        {%- else %}
        pass
        {%- endif %}
    {%- endfor -%}
