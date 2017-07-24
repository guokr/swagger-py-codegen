# -*- coding: utf-8 -*-

# TODO: datetime support

{% include '_do_not_change.tpl' %}

base_path = '{{base_path}}'

{% for name, value in schemas.items() %}
{{ name }} = {{ value }}
{%- endfor %}

validators = {
{%- for name, value in validators.items() %}
    {{ name }}: {{ value }},
{%- endfor %}
}

filters = {
{%- for name, value in filters.items() %}
    {{ name }}: {{ value }},
{%- endfor %}
}

scopes = {
{%- for name, value in scopes.items() %}
    {{ name }}: {{ value }},
{%- endfor %}
}


class Current(object):

    request = None


current = Current()


class Security(object):

    def __init__(self):
        super(Security, self).__init__()
        self._loader = lambda x: []

    @property
    def scopes(self):
        return self._loader(current.request)

    def scopes_loader(self, func):
        self._loader = func
        return func

security = Security()


{{ merge_default }}

{{ normalize }}

