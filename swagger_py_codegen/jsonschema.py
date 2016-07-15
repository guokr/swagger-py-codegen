from collections import OrderedDict
from inspect import getsource

from .base import Code, CodeGenerator
from .parser import schema_var_name


class Schema(Code):

    template = 'jsonschema/schemas.tpl'
    dest_template = '%(package)s/%(module)s/schemas.py'
    override = True


def _parameters_to_schemas(params):
    locations = ['body', 'header', 'formData', 'query']
    for location in locations:
        required = []
        properties = {}
        type_ = 'object'
        for param in params:
            if param.get('in') != location:
                continue
            if location == 'body':
                # schema is required `in` is `body`
                yield location, param['schema']
                continue

            prop = param.copy()
            prop.pop('in')
            if param.get('required'):
                required.append(param['name'])
                prop.pop('required')
            properties[prop['name']] = prop
            prop.pop('name')
        if len(properties) == 0:
            continue
        yield location, dict(required=required, properties=properties)


def build_data(swagger):

    validators = OrderedDict()  # (endpoint, method) = {'body': schema_name or schema, 'query': schema_name, ..}
    filters = OrderedDict()  # (endpoint, method) = {'200': {'schema':, 'headers':, 'examples':}, 'default': ..}
    scopes = OrderedDict()  # (endpoint, method) = [scope_a, scope_b]

    # path parameters
    for path, _ in swagger.search(['paths', '*']):
        path_param = []
        try:
            path_param = swagger.get(path + ('parameters',))
        except KeyError:
            pass

        # methods
        for p, data in swagger.search(path + ('*',)):
            if p[-1] not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                continue
            method_param = []
            try:
                method_param = swagger.get(p + ('parameters',))
            except KeyError:
                pass

            endpoint = p[1]  # p: ('paths', '/some/path', 'method')
            method = p[-1].upper()

            # parameters as schema
            validator = dict(_parameters_to_schemas(path_param + method_param))
            if validator:
                validators[(endpoint, method)] = validator

            # responses
            responses = data.get('responses')
            if responses:
                filter = {}
                for status, res_data in responses.iteritems():
                    if isinstance(status, int) or status.isdigit():
                        filter[int(status)] = dict(
                            headers=res_data.get('headers'),
                            schema=res_data.get('schema')
                        )
                filters[(endpoint, method)] = filter

            # scopes
            for security in data.get('security', []):
                scopes[(endpoint, method)] = security.values().pop()
                break

    schemas = OrderedDict([(schema_var_name(path), swagger.get(path)) for path in swagger.definitions])

    data = dict(
        schemas=schemas,
        validators=validators,
        filters=filters,
        scopes=scopes,
        merge_default=getsource(merge_default),
        normalize=getsource(normalize)
    )
    return data


class SchemaGenerator(CodeGenerator):

    def _process(self):
        yield Schema(build_data(self.swagger))


def merge_default(schema, value):
    # TODO: more types support
    type_defaults = {
        'integer': 9573,
        'string': 'something',
        'object': {},
        'array': [],
        'boolean': False
    }

    return normalize(schema, value, type_defaults)[0]


def build_default(schema):
    return merge_default(schema, None)


def normalize(schema, data, required_defaults=None):

    if required_defaults is None:
        required_defaults = {}
    errors = []

    class DataWrapper(object):

        def __init__(self, data):
            super(DataWrapper, self).__init__()
            self.data = data

        def get(self, key, default=None):
            if isinstance(self.data, dict):
                return self.data.get(key, default)
            return getattr(self.data, key, default)

        def has(self, key):
            if isinstance(self.data, dict):
                return key in self.data
            return hasattr(self.data, key)

        def keys(self):
            if isinstance(self.data, dict):
                return self.data.keys()
            return vars(self.data).keys()

        def get_check(self, key, default=None):
            if isinstance(self.data, dict):
                value = self.data.get(key, default)
                has_key = key in self.data
            else:
                try:
                    value = getattr(self.data, key)
                except AttributeError:
                    value = default
                    has_key = False
                else:
                    has_key = True
            return value, has_key

    def _normalize_dict(schema, data):
        result = {}
        if not isinstance(data, DataWrapper):
            data = DataWrapper(data)

        for key, _schema in schema.get('properties', {}).iteritems():
            # set default
            type_ = _schema.get('type', 'object')
            if ('default' not in _schema
                    and key in schema.get('required', [])
                    and type_ in required_defaults):
                _schema['default'] = required_defaults[type_]

            # get value
            value, has_key = data.get_check(key)
            if has_key:
                result[key] = _normalize(_schema, value)
            elif 'default' in _schema:
                result[key] = _schema['default']
            elif key in schema.get('required', []):
                errors.append(dict(name='property_missing',
                                   message='`%s` is required' % key))

        for _schema in schema.get('allOf', []):
            rs_component = _normalize(_schema, data)
            rs_component.update(result)
            result = rs_component

        additional_properties_schema = schema.get('additionalProperties', False)
        if additional_properties_schema:
            aproperties_set = set(data.keys()) - set(result.keys())
            for pro in aproperties_set:
                result[pro] = _normalize(additional_properties_schema, data.get(pro))

        return result

    def _normalize_list(schema, data):
        result = []
        if hasattr(data, '__iter__') and not isinstance(data, dict):
            for item in data:
                result.append(_normalize(schema.get('items'), item))
        elif 'default' in schema:
            result = schema['default']
        return result

    def _normalize_default(schema, data):
        if data is None:
            return schema.get('default')
        else:
            return data

    def _normalize(schema, data):
        if not schema:
            return None
        funcs = {
            'object': _normalize_dict,
            'array': _normalize_list,
            'default': _normalize_default,
        }
        type_ = schema.get('type', 'object')
        if not type_ in funcs:
            type_ = 'default'

        return funcs[type_](schema, data)

    return _normalize(schema, data), errors
