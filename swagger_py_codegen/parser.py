# -*- coding: utf-8 -*-
import string
import dpath.util


def schema_var_name(path):
    return ''.join(map(string.capitalize, path))


class RefNode(dict):

    def __init__(self, data, ref):
        self.ref = ref
        super(RefNode, self).__init__(data)

    def __repr__(self):
        return schema_var_name(self.ref)


class Swagger(object):

    separator = '\0'

    def __init__(self, data):
        self.data = data
        self._definitions = []
        for path, _ in self.search(['definitions', '*']):
            self._definitions.append(path)
        self._process_ref()

    def _process_ref(self):
        for path, ref in self.search(['**', '$ref']):
            ref = ref.lstrip('#/').split('/')
            ref = tuple(ref)
            data = self.get(ref)

            if ref in self._definitions:
                self._definitions.remove(ref)
            self._definitions.insert(0, ref)

            path = path[:-1]
            self.set(path, RefNode(data, ref))

    def search(self, path):
        for p, d in dpath.util.search(self.data, list(path), True, self.separator):
            yield tuple(p.split(self.separator)), d

    def get(self, path):
        return dpath.util.get(self.data, list(path))

    def set(self, path, data):
        dpath.util.set(self.data, list(path), data)

    @property
    def definitions(self):
        return self._definitions

    @property
    def scopes_supported(self):
        for _, data in self.search(['securityDefinitions', '*', 'scopes']):
            return data.keys()
        return []

    @property
    def module_name(self):
        return self.base_path.strip('/').replace('/', '_')

    @property
    def base_path(self):
        return self.data.get('basePath', '/v1')