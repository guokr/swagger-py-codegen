# -*- coding: utf-8 -*-

# TODO: datetime support

{% include '_do_not_change.tpl' %}

{% for name, value in schemas.iteritems() %}
{{ name }} = {{ value }}
{%- endfor %}

validators = {
{%- for name, value in validators.iteritems() %}
    {{ name }}: {{ value }},
{%- endfor %}
}

filters = {
{%- for name, value in filters.iteritems() %}
    {{ name }}: {{ value }},
{%- endfor %}
}

scopes = {
{%- for name, value in scopes.iteritems() %}
    {{ name }}: {{ value }},
{%- endfor %}
}


class Security(object):

    def __init__(self):
        super(Security, self).__init__()
        self._loader = lambda: []

    @property
    def scopes(self):
        return self._loader()

    def scopes_loader(self, func):
        self._loader = func
        return func

security = Security()


{{ merge_default }}

{{ normalize }}

