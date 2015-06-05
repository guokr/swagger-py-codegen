# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas


class {{ name }}(Resource):

    {%- for method, ins in methods.iteritems() %}

    def {{ method.lower() }}(self{{ params.__len__() and ', ' or '' }}{{ params | join(', ') }}):
        {%- for request in ins.requests %}
        print g.{{ request }}
        {%- endfor %}

        {% if 'response' in  ins -%}
        return {{ ins.response.0 }}, {{ ins.response.1 }}, {{ ins.response.2 }}
        {%- else %}
        pass
        {%- endif %}
    {%- endfor -%}
