# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}
from __future__ import absolute_import, print_function

{% for view in views -%}
from .api.{{ view.endpoint }} import {{ view.name }}
{% endfor %}

routes = [
    {%- for view in views %}
    dict(resource={{ view.name }}(), url='{{ view.url }}'),
    {%- endfor %}
]
