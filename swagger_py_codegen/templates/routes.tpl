# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

{% for _, res in resources.iteritems() -%}
from .api.{{ res.path_name }} import {{ res.class_name }}
{% endfor %}

routes = [
    {%- for route in routes %}
    {{ route }},
    {%- endfor %}
]
