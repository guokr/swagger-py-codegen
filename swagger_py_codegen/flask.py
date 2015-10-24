import re
from collections import OrderedDict

from .base import Code, CodeGenerator
from .jsonschema import Schema, SchemaGenerator, build_default

SUPPORT_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']


class Router(Code):

    template = 'flask/routers.tpl'
    dest_template = '%(package)s/%(module)s/routes.py'
    override = True


class View(Code):

    template = 'flask/view.tpl'
    dest_template = '%(package)s/%(module)s/api/%(view)s.py'
    override = False


class Specification(Code):

    template = 'flask/specification.tpl'
    dest_template = '%(package)s/static/%(module)s/swagger.json'
    override = True


class Validator(Code):

    template = 'flask/validators.tpl'
    dest_template = '%(package)s/%(module)s/validators.py'
    override = True


class Api(Code):

    template = 'flask/api.tpl'
    dest_template = '%(package)s/%(module)s/api/__init__.py'


class Blueprint(Code):

    template = 'flask/blueprint.tpl'
    dest_template = '%(package)s/%(module)s/__init__.py'


class App(Code):

    template = 'flask/app.tpl'
    dest_template = '%(package)s/__init__.py'


class Requirements(Code):

    template = 'flask/requirements.tpl'
    dest_template = 'requirements.txt'


class UIIndex(Code):

    template = 'ui/index.html'
    dest_template = '%(package)s/static/swagger-ui/index.html'


def _swagger_to_flask_url(url, swagger_path_node):
    types = {
        'integer': 'int',
        'long': 'int',
        'float': 'float',
        'double': 'float'
    }
    node = swagger_path_node
    params = re.findall(r'\{([^\}]+?)\}', url)
    url = re.sub(r'{(.*?)}', '<\\1>', url)

    def _type(parameters):
        for p in parameters:
            if p.get('in') != 'path':
                continue
            t = p.get('type', 'string')
            if t in types:
                yield '<%s>' % p['name'], '<%s:%s>' % (types[t], p['name'])

    for old, new in _type(node.get('parameters', [])):
        url = url.replace(old, new)

    for k in SUPPORT_METHODS:
        if k in node:
            for old, new in _type(node[k].get('parameters', [])):
                url = url.replace(old, new)

    return url, params


def _path_to_endpoint(swagger_path):
    return swagger_path.strip('/').replace('/', '_').replace('-', '_').translate(None, '{}')


def _path_to_resource_name(swagger_path):
    return swagger_path.title().translate(None, '{}/_-')


def _location(swagger_location):
    location_map = {
        'body': 'json',
        'header': 'headers',
        'formData': 'form',
        'query': 'args'
    }
    return location_map.get(swagger_location)


class FlaskGenerator(CodeGenerator):

    dependencies = [SchemaGenerator]

    def __init__(self, swagger):
        super(FlaskGenerator, self).__init__(swagger)
        self.with_spec = False
        self.with_ui = False

    def _dependence_callback(self, code):
        if not isinstance(code, Schema):
            return code
        schemas = code
        # schemas default key likes `('/some/path/{param}', 'method')`
        # use flask endpoint to replace default validator's key,
        # example: `('some_path_param', 'method')`
        validators = OrderedDict()
        for k, v in schemas.data['validators'].iteritems():
            locations = {_location(loc): val for loc, val in v.iteritems()}
            validators[(_path_to_endpoint(k[0]), k[1])] = locations

        # filters
        filters = OrderedDict()
        for k, v in schemas.data['filters'].iteritems():
            filters[(_path_to_endpoint(k[0]), k[1])] = v

        # scopes
        scopes = OrderedDict()
        for k, v in schemas.data['scopes'].iteritems():
            scopes[(_path_to_endpoint(k[0]), k[1])] = v

        schemas.data['validators'] = validators
        schemas.data['filters'] = filters
        schemas.data['scopes'] = scopes
        self.schemas = schemas
        self.validators = validators
        self.filters = filters
        return schemas

    def _process_data(self):

        views = []  # [{'endpoint':, 'name':, url: '', params: [], methods: {'get': {'requests': [], 'response'}}}, ..]

        for paths, data in self.swagger.search(['paths', '*']):
            swagger_path = paths[-1]
            url, params = _swagger_to_flask_url(swagger_path, data)
            endpoint = _path_to_endpoint(swagger_path)
            name = _path_to_resource_name(swagger_path)

            methods = OrderedDict()
            for method in SUPPORT_METHODS:
                if method not in data:
                    continue
                methods[method] = {}
                validator = self.validators.get((endpoint, method.upper()))
                if validator:
                    methods[method]['requests'] = validator.keys()

                for status, res_data in data[method].get('responses', {}).iteritems():
                    if isinstance(status, int) or status.isdigit():
                        example = res_data.get('schema', {}).get('application/json')
                        if not example:
                            example = build_default(res_data.get('schema'))
                        response = example, int(status), build_default(res_data.get('headers'))
                        methods[method]['response'] = response
                        break

            views.append(dict(
                url=url,
                params=params,
                endpoint=endpoint,
                methods=methods,
                name=name
            ))

        return views

    def _get_oauth_scopes(self):
        for path, scopes in self.swagger.search(('securityDefinitions', '*', 'scopes')):
            return scopes
        return None

    def _process(self):
        views = self._process_data()
        yield Router(dict(views=views))
        for view in views:
            yield View(view, dist_env=dict(view=view['endpoint']))
        if self.with_spec:
            try:
                import simplejson as json
            except ImportError:
                import json
            swagger = {}
            swagger.update(self.swagger.origin_data)
            swagger.pop('host', None)
            swagger.pop('schemes', None)
            yield Specification(dict(swagger=json.dumps(swagger, indent=2)))

        yield Validator()

        yield Api()

        yield Blueprint(dict(scopes_supported=self.swagger.scopes_supported,
                             blueprint=self.swagger.module_name))
        yield App(dict(blueprint=self.swagger.module_name,
                       base_path=self.swagger.base_path))

        yield Requirements()

        if self.with_ui:
            yield UIIndex(dict(spec_path='/static/%s/swagger.json' % self.swagger.module_name))
