# -*- coding: utf-8 -*-
from flask import request, g

from . import Resource
from .. import schemas

{%- for res in resources %}


class {{ res.class_name }}(Resource):

    {%- for method, ins in res.methods.iteritems() %}

    def {{ method.lower() }}(self{{ ins.path_params.__len__() and ', ' or '' }}{{ ins.path_params | join(', ') }}):
        {%- for loc in ins.request_locations %}
        print g.{{ loc }}
        {%- endfor -%}
        {%- if ins.response_filter %}

        return {{ ins.response_filter.many and '[' or '' }}
        {{- ins.response_filter.schema.default_value -}}
        {{ ins.response_filter.many and ']' or '' }}, {{ ins.response_filter.code }}
        {%- endif -%}
    {%- endfor -%}
{%- endfor %}
