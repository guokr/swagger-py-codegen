from __future__ import absolute_import

import copy

import six
from collections import OrderedDict
from inspect import getsource

from .base import Code, CodeGenerator
from .parser import RefNode


class Schema(Code):
    template = 'jsonschema/schemas.tpl'
    dest_template = '%(package)s/%(module)s/schemas.py'
    override = True


def _parameters_to_schemas(params):
    locations = ['body', 'header', 'formData', 'query']
    for location in locations:
        required = []
        properties = {}
        for param in params:
            if param.get('in') != location:
                continue
            if location == 'body':
                # schema is required `in` is `body`
                yield location, param['schema']
                continue
            # prop = param.copy()
            # If the parameter is referanced more than once,it would be format only once.
            prop = copy.deepcopy(param)
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
            #print 'parameters:::::::::::::', path_param, endpoint, method, validator, method_param
            if validator:
                validators[(endpoint, method)] = validator

            # responses
            responses = data.get('responses')
            if responses:
                filter = {}
                for status, res_data in six.iteritems(responses):
                    if isinstance(status, int) or status.isdigit():
                        filter[int(status)] = dict(
                            headers=res_data.get('headers'),
                            schema=res_data.get('schema')
                        )
                filters[(endpoint, method)] = filter

            # scopes
            for security in data.get('security', []):
                scopes[(endpoint, method)] = list(security.values()).pop()
                break
    data = dict(
        definitions={'definitions': swagger.origin_data.get('definitions', {}),
                     'parameters': swagger.origin_data.get('parameters', {})},
        validators=validators,
        filters=filters,
        scopes=scopes,
        base_path=swagger.base_path,
        merge_default=getsource(merge_default),
        normalize=getsource(normalize)
    )
    return data


class SchemaGenerator(CodeGenerator):

    def _process(self):
        yield Schema(build_data(self.swagger))


def merge_default(schema, value, get_first=True, resolver=None):
    # TODO: more types support
    type_defaults = {
        'integer': 9573,
        'string': 'something',
        'object': {},
        'array': [],
        'boolean': False
    }

    results = normalize(schema, value, type_defaults, resolver=resolver)
    if get_first:
        return results[0]
    return results


def build_default(schema, resolver=None):
    return merge_default(schema, None, resolver=resolver)


def normalize(schema, data, required_defaults=None, resolver=None):
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
                return list(self.data.keys())
            return list(getattr(self.data, '__dict__', {}).keys())

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

    def _merge_dict(src, dst):
        for k, v in six.iteritems(dst):
            if isinstance(src, dict):
                if isinstance(v, dict):
                    r = _merge_dict(src.get(k, {}), v)
                    src[k] = r
                else:
                    src[k] = v
            else:
                src = {k: v}
        return src

    def _normalize_dict(schema, data):
        result = {}
        if not isinstance(data, DataWrapper):
            data = DataWrapper(data)

        for _schema in schema.get('allOf', []):
            rs_component = _normalize(_schema, data)
            _merge_dict(result, rs_component)

        for key, _schema in six.iteritems(schema.get('properties', {})):
            # set default
            type_ = _schema.get('type', 'object')

            # get value
            value, has_key = data.get_check(key)
            if has_key and '$ref' in _schema:
                result[key] = _normalize(_schema, value)
            elif has_key:
                result[key] = _normalize(_schema, value)
            elif 'default' in _schema:
                result[key] = _schema['default']
            elif key in schema.get('required', []):
                if type_ in required_defaults:
                    result[key] = required_defaults[type_]
                else:
                    errors.append(dict(name='property_missing',
                                       message='`%s` is required' % key))

        additional_properties_schema = schema.get('additionalProperties', False)
        if additional_properties_schema is not False:
            aproperties_set = set(data.keys()) - set(result.keys())
            for pro in aproperties_set:
                result[pro] = _normalize(additional_properties_schema, data.get(pro))

        return result

    def _normalize_list(schema, data):
        result = []
        if hasattr(data, '__iter__') and not isinstance(data, (dict, RefNode)):
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

    def _normalize_ref(schema, data):
        if resolver == None:
            raise TypeError("resolver must be provided")
        ref = schema.get(u"$ref")
        scope, resolved = resolver.resolve(ref)
        if resolved.get('nullable', False) and not data:
            return {}
        return _normalize(resolved, data)

    def _normalize(schema, data):
        if schema is True or schema == {}:
            return data
        if not schema:
            return None
        funcs = {
            'object': _normalize_dict,
            'array': _normalize_list,
            'default': _normalize_default,
            'ref': _normalize_ref
        }
        type_ = schema.get('type', 'object')
        if type_ not in funcs:
            type_ = 'default'
        if schema.get(u'$ref', None):
            type_ = 'ref'

        return funcs[type_](schema, data)

    return _normalize(schema, data), errors
