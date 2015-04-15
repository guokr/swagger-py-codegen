# -*- coding: utf-8 -*-

{% include '_do_not_change.tpl' %}

from marshmallow import Schema, fields, validate

{%- for name, schema in schemas.iteritems() %}


class {{ name }}Schema(Schema):
     {%- for n, field in schema.fields.iteritems() %}
     {{ n }} = {{ field }}
     {%- endfor %}

{%- endfor %}

