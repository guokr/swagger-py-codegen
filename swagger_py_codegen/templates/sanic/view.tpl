# -*- coding: utf-8 -*-

from sanic.response import text

from . import Resource
from .. import schemas


class {{ name }}(Resource):

    {%- for method, ins in methods.items() %}

    async def {{ method.lower() }}(self, request{{ params.__len__() and ', ' or '' }}{{ params | join(', ') }}):
        {%- for request in ins.requests %}
        print(request.{{request}})
        {%- endfor %}

        {% if 'response' in  ins -%}
        return {{ ins.response.0 }}, {{ ins.response.1 }}, {{ ins.response.2 }}
        {%- else %}
        pass
        {%- endif %}
    {%- endfor -%}
