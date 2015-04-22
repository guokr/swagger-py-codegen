# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
import operator
from .model import (
    SwaggerFlaskModel,
    Schema, Field, Resource,
    Method, ResponseFilter,
    Validator)


class SchemaResolver(object):

    def __init__(self, name, data):
        super(SchemaResolver, self).__init__()
        self.name = name
        self.data = data

    def resolve(self):
        name, data = self.name, self.data
        s = Schema(name)
        for k, v in data['properties'].iteritems():
            if k in data.get('required', []):
                v['required'] = True
            s.add_field(k, FieldResolver(v).resolve())
        return s


class FieldResolver(object):

    type_map = {
        'string': 'String',
        'integer': 'Integer',
        'number': 'Float',
        'boolean': 'Boolean',
        'array': 'List'
    }
    format_map = {
        'int32': 'Integer',
        'int64': 'Integer',
        'float': 'Float',
        'double': 'Decimal',
        'decimal': 'Decimal',
        'formattedString': 'FormattedString',
        'date': 'Date',
        'time': 'Time',
        'datetime': 'DateTime',
        'timedelta': 'TimeDelta',
        'fixed': 'Fixed',
        'price': 'Price',
        'uuid': 'UUID',
        'url': 'Url',
        'email': 'Email'
    }

    common_attrs_map = {
        'default': 'default',
        'required': 'required'
    }

    def __init__(self, data):
        super(FieldResolver, self).__init__()
        self.data = data
        t = self._get_type()
        self.field = Field(t)

    def _get_type(self):
        t = self.type_map[self.data.get('type', 'string')]
        if 'format' in self.data:
            t = self.format_map[self.data['format']]
        if 'enum' in self.data:
            t = 'Enum'
        if 'items' in self.data:
            if isinstance(self.data['items'], basestring):
                t = 'Nested'
            else:
                t = 'List'
        return t

    def _get_attrs(self):
        args = []
        kwargs = {}
        if self.field.type == 'List':
            f = FieldResolver(self.data['items']).resolve()
            kwargs['cls_or_instance'] = f
        if self.field.type == 'Nested':
            # just for generate schema name..
            f = Schema(self.data['items'])
            kwargs['nested'] = f
        if self.field.type in ['Enum', 'Select']:
            kwargs['choices'] = self.data.get('enum', [])
        for k, v in self.common_attrs_map.iteritems():
            if k in self.data:
                kwargs[v] = self.data[k]
        # TODO: init validators from data
        return args, kwargs

    def resolve(self):
        self.field.args, self.field.kwargs = self._get_attrs()
        return self.field


class MethodResolver(object):

    locations_map = {
        'body': 'json',
        'header': 'headers',
        'formData': 'form',
        'query': 'args'
    }

    params_schema_common_parts = [
        'type',
        'description',
        'format',
        'items',
        'collectionFormat',
        'default',
        'maximum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'maxItems',
        'minItems',
        'uniqueItems',
        'enum',
        'multipleOf'
    ]

    def __init__(self, method, data, parent):
        super(MethodResolver, self).__init__()
        self.method = method
        self.data = data
        self.parent = parent

    def _process_schema(self, location, params):
        name = '%s%s%s' % (
            self.parent.name, self.method.upper(), location.title())
        data = {
            'required': [],
            'properties': {}
        }
        common = self.params_schema_common_parts
        for p in params:
            if 'schema' in p:
                many = False
                schema = p['schema']
                if isinstance(p['schema'], dict):
                    many = True
                    schema = p['schema']['items']
                return Validator(
                    self.parent.parent.schemas[schema],
                    many)
            data['properties'][p['name']] = {
                c: p[c] for c in common if c in p
            }
            if p.get('required', False):
                data['required'].append(p['name'])
        s = SchemaResolver(name, data).resolve()
        self.parent.parent.add_schema(s)
        return Validator(s, False)

    def resolve(self):
        m = Method(self.method, self.parent)
        # requests
        group = {}
        for p in self.data.get('parameters', []):
            group.setdefault(p['in'], [])
            group[p['in']].append(p)
        for loc, params in group.iteritems():
            if loc not in self.locations_map:
                continue
            location = self.locations_map[loc]
            validator = self._process_schema(location, params)
            m.request_location_schemas[location] = validator
        # response
        for code, r in self.data.get('responses').iteritems():
            if isinstance(code, int) and 'schema' in r:
                name = r['schema']
                many = False
                if isinstance(r['schema'], dict):
                    name = r['schema']['items']
                    many = True
                schema = self.parent.parent.schemas[name]
                m.response_filter = ResponseFilter(code, schema, many)
        return m


class ResourceResolver(object):

    path_type_mapper = {
        'integer': 'int',
        'long': 'int',
        'float': 'float',
        'double': 'float'
    }
    support_methods = ['get', 'put', 'post', 'delete', 'patch']

    def __init__(self, path, data, parent):
        super(ResourceResolver, self).__init__()
        self.path = path
        self.data = data
        self.parent = parent

    def _get_url(self):
        url = self.path
        url = re.sub(r'{(.*?)}', '<\\1>', url)
        for p in self.data.get('parameters', {}).get('path', {}):
            if p.type in self.path_type_mapper:
                t = self.path_type_mapper[p.type]
                url.replace('<%s>' % p.name, '<%s:%s>' % (t, p.name))
        return url

    def resolve(self):
        url = self._get_url()
        resource = Resource(url, self.parent)

        results = {}
        for method, data in self.data.iteritems():
            if method not in self.support_methods:
                continue
            m = MethodResolver(method, data, resource).resolve()
            results[method.upper()] = m
        resource.methods = results
        return resource


class FlaskModelResolver(object):

    def __init__(self, swagger):
        super(FlaskModelResolver, self).__init__()
        self.swagger = swagger
        self.model = None

    def resolve(self):
        self.model = SwaggerFlaskModel()
        self.model.blueprint = self.swagger.get('basePath', 'v1').strip('/')

        self._resolve_schemas()
        self._resolve_resources()
        self._sort_schemas()
        return self.model

    def _resolve_schemas(self):
        for name, d in self.swagger['definitions'].iteritems():
            s = SchemaResolver(name, d).resolve()
            self.model.add_schema(s)

    def _resolve_resources(self):
        for path, d in self.swagger['paths'].iteritems():
            r = ResourceResolver(path, d, self.model).resolve()
            self.model.add_resource(r)

    def _sort_schemas(self):
        orders = dict(zip(self.model.schemas.keys(), [0] * len(self.model.schemas)))

        def count(n):
            orders[n] += 1
            for f in self.model.schemas[n].fields.values():
                if 'nested' in f.kwargs:
                    count(f.kwargs['nested'].name)

        [count(name) for name in self.model.schemas.keys()]
        schemas = OrderedDict()
        for k, v in sorted(orders.items(), key=operator.itemgetter(1), reverse=True):
            schemas[k] = self.model.schemas[k]
        self.model.schemas = schemas
