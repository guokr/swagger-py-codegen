# -*- coding: utf-8 -*-
import yaml
from .resolver import FlaskModelResolver


class Swagger(dict):

    def get_by_ref(self, ref):
        host, path = ref.split('#/')
        # TODO: load from remote host
        return self.get_by_keys(path.split('/'))

    def get_by_keys(self, keys):
        return reduce(lambda o, k: o[k], keys, self)

    def set_by_keys(self, keys, value):
        self.get_by_keys(keys[:-1])[keys[-1]] = value


class SwaggerParser(object):

    def __init__(self):
        super(SwaggerParser, self).__init__()
        self.swagger = None

    def parse_yaml(self, yml):
        return self.parse(yaml.load(yml))

    def parse(self, content):
        self.swagger = Swagger(content)
        self._resolve_refs()
        return self.swagger

    def _resolve_refs(self):
        self._walk(self.swagger, [])

    def _walk(self, node, paths):
        paths = list(paths)
        if isinstance(node, dict):
            if '$ref' in node:
                if paths[-1] in ('schema', 'items'):
                    self.swagger.set_by_keys(
                        paths, node['$ref'].split('/')[-1])
                else:
                    self.swagger.set_by_keys(
                        paths, self.swagger.get_by_ref(node['$ref']))
                return
            for k, v in node.iteritems():
                self._walk(v, paths + [k])
        elif isinstance(node, list) and not isinstance(node, basestring):
            for k, v in enumerate(node):
                self._walk(v, paths + [k])


def parse_yaml(yaml_content):
    swagger = SwaggerParser().parse_yaml(yaml_content)
    return FlaskModelResolver(swagger).resolve()
