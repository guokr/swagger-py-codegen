# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}
from __future__ import absolute_import

{% for view in views -%}
from .api.{{ view.endpoint }} import {{ view.name }}
{% endfor %}

url_prefix = '{{ blueprint }}'

routes = [
    {%- for view in views %}
    dict(resource={{ view.name }}, urls=[r"{{ view.url }}"], endpoint='{{ view.endpoint }}'),
    {%- endfor %}
]

def load_uris(config):
    try:
        config.update_uri(routes, url_prefix)
    except:
        pass