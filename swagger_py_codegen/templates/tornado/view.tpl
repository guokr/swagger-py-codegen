# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from . import ApiHandler
from .. import schemas


class {{ name }}(ApiHandler):

    {%- for method, ins in methods.items() %}

    def {{ method.lower() }}(self{{ params.__len__() and ', ' or '' }}{{ params | join(', ') }}):
        {%- for request in ins.requests %}
        print(self.{{ request }})
        {%- endfor %}

        {% if 'response' in  ins -%}
        return {{ ins.response.0 }}, {{ ins.response.1 }}, {{ ins.response.2 }}
        {%- else %}
        pass
        {%- endif %}
    {%- endfor -%}

