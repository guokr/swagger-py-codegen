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
        object_to_dict=getsource(object_to_dict)
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
    type_ = schema.get('type', 'object')

    if not schema:
        return None

    if type_ == 'object':
        result = type_defaults.get(type_)
        default = schema.get('default', {})
        default.update(value or {})
        for name, property_ in schema.get('properties', {}).iteritems():
            if (name in default 
                    or 'default' in property_ 
                    or name in schema.get('required', [])
                    or property_.get('type') in ('object', 'array')):
                result[name] = merge_default(property_, default.get(name))
    elif type_ == 'array':
        result = type_defaults.get(type_)
        if 'default' in schema:
            result = schema.get('default', [])
        elif value and isinstance(value, list):
            result = value
        else:
            item = build_default(schema.get('items'))
            result.append(item)
    else:
        result = value or schema.get('default') or type_defaults.get(type_)

    return result


def build_default(schema):
    return merge_default(schema, None)


def object_to_dict(schema, obj):
    if isinstance(obj, dict):
        return obj, []
    if not schema:
        return None, []
    data = {}
    errors = []
    required = schema.get('required', [])
    for name, property_ in schema.get('properties', {}).iteritems():
        if hasattr(obj, name):
            if 'properties' in property_:
                data[name], errs = object_to_dict(property_, getattr(obj, name))
                errors.extend(errs)
            else:
                data[name] = getattr(obj, name)
        elif 'default' in property_:
            data[name] = property_['default']
        elif 'items' in property_ and 'default' in property_['items']:
            data[name] = [property_['items']['default']]
        elif name in required:
            errors.append(dict(name='property_missing',
                               message='`%s` is required' % name))
    return data, errors

