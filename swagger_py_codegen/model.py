# -*- coding: utf-8 -*-
import re
from collections import OrderedDict, namedtuple


class Field(object):

    default_values = {
        'String': 'poooo',
        'Integer': 9263,
        'Float': 83.75,
        'Decimal': 83.7578,
        'FormattedString': 'hello {name}'
    }

    fields_module = 'fields'

    def __init__(self, type_=None, args=None, kwargs=None):
        super(Field, self).__init__()
        self.type = type_
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

    @property
    def is_list(self):
        return self.type == 'List'

    @property
    def default_value(self):
        if self.is_list:
            return [self.kwargs['cls_or_instance'].default_value]
        default = self.kwargs.get('default')
        if not default and self.type in ['Enum', 'Select']:
            default = self.kwargs.get('choices')[0]
        if not default:
            return self.default_values.get(self.type, 'nullll')
        return default

    @classmethod
    def field_name(cls, name):
        return name if name != cls.fields_module else '_%s' % name

    def __repr__(self):
        args = self.args + ['%s=%r' % (k, v)
                            for k, v in self.kwargs.iteritems()]
        return '%s.%s(%s)' % (self.fields_module,
                              self.type, ', '.join([str(a) for a in args]))

    __str__ = __repr__


class Schema(object):

    def __init__(self, name):
        super(Schema, self).__init__()
        self.name = name
        self.fields = {}

    def add_field(self, name, field):
        name = Field.field_name(name)
        self.fields[name] = field

    @property
    def class_name(self):
        return self.name + 'Schema'

    @property
    def default_value(self):
        return dict([(n, f.default_value) for n, f in self.fields.iteritems()])

    def __repr__(self):
        return self.class_name

    __str__ = __repr__


ResponseFilter = namedtuple('ResponseFilter', ['code', 'schema', 'many'])
Validator = namedtuple('Validator', ['schema', 'many'])


class Method(object):

    def __init__(self, name, parent):
        super(Method, self).__init__()
        self.parent = parent
        self.name = name.upper()
        self.request_location_schemas = {}
        self.response_filter = None

    @property
    def title(self):
        return self.name

    @property
    def request_locations(self):
        return self.request_location_schemas.keys()

    @property
    def path_params(self):
        return self.parent.path_params


class Resource(object):

    def __init__(self, url, parent, methods=None):
        super(Resource, self).__init__()
        self.url = url
        self.parent = parent
        self.methods = methods if methods else {}

    @property
    def urls(self):
        return [self.url]

    @property
    def name(self):
        url = re.sub(r'<(.*:)?(.*?)>', r'\2', self.url)
        return url.title().translate(None, '<>/_:')

    @property
    def title(self):
        return self.name

    @property
    def class_name(self):
        return self.name

    @property
    def endpoint(self):
        return self.url.strip('/').replace('/', '_').translate(None, '<>:')

    @property
    def path_params(self):
        return map(lambda x: x[1], re.findall(r'<(.*:)?(.*?)>', self.url))

    @property
    def root_path(self):
        return self.url.split('/')[1].translate(None, '<>:')

    def __repr__(self):
        return self.class_name

    __str__ = __repr__


class SwaggerFlaskModel(object):

    def __init__(self):
        super(SwaggerFlaskModel, self).__init__()
        self.schemas = OrderedDict()
        # self.schemas = {}
        self.resources_group = OrderedDict()
        self.blueprint = ''

    def add_resource(self, resource):
        self.resources_group.setdefault(resource.root_path, [])
        self.resources_group[resource.root_path].append(resource)

    def add_schema(self, schema):
        self.schemas[schema.name] = schema

    @property
    def routes(self):
        routes = []
        for _, res in self.resources.iteritems():
            routes.append(
                dict(resource=res, urls=res.urls, endpoint=res.endpoint))
        return routes

    @property
    def resources(self):
        d = OrderedDict()
        for _, ins in self.resources_group.iteritems():
            for r in ins:
                d[r.class_name] = r
        return d

    @property
    def validators(self):
        validators = {}
        for res in self.resources.values():
            for ins in res.methods.values():
                for loc, schema in ins.request_location_schemas.iteritems():
                    validators[(ins.parent.endpoint, ins.name, loc)] = schema
        return validators

    @property
    def filters(self):
        filters = {}
        for res in self.resources.values():
            for ins in res.methods.values():
                if ins.response_filter:
                    filters[
                        (ins.parent.endpoint, ins.name)] = ins.response_filter
        return filters
