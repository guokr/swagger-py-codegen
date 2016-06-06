# -*- coding: utf-8 -*-
import string
import copy
import dpath.util
import sys

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

    def __init__(self, data, pool=None):
        self.data = data
        self.origin_data = copy.deepcopy(data)
        self._definitions = []
        self._references_sort()
        self._get_cached = {}
        if pool:
            process_references(self, pool)
        else:
            self._process_ref()

    def _process_ref(self):

        for path, ref in self.search(['**', '$ref']):
            ref = ref.lstrip('#/').split('/')
            ref = tuple(ref)
            data = self.get(ref)

            path = path[:-1]
            self.set(path, RefNode(data, ref))

    def _references_sort(self):

        def get_definition_refs():
            definition_refs_default = {}
            definition_refs = {}
            for path, _ in self.search(['definitions', '*']):
                definition_refs_default[path] = set([])
            for path, ref in self.search(['definitions', '**', '$ref']):
                schema = tuple(path[0:2])
                ref = ref.lstrip('#/').split('/')
                ref = tuple(ref)

                if schema in definition_refs.keys():
                    definition_refs[schema].add(ref)
                else:
                    definition_refs[schema] = set([ref])

            definition_refs_default.update(definition_refs)
            return definition_refs_default

        definition_refs = get_definition_refs()
        while definition_refs:
            ready = {definition for definition, refs in definition_refs.iteritems() if not refs}
            if not ready:
                msg = '$ref circular references found!\n'
                raise ValueError(msg)
            for definition in ready:
                del definition_refs[definition]
            for refs in definition_refs.itervalues():
                refs.difference_update(ready)

            self._definitions += ready

    def search(self, path):
        for p, d in dpath.util.search(self.data, list(path), True, self.separator):
            yield tuple(p.split(self.separator)), d

    def pickle_search(self, path):
        for p, d in dpath.util.search(self.data, list(path), True,
                                      self.separator):
            yield (self, tuple(p.split(self.separator)), d)

    def get(self, path):
        key = ''.join(path)
        if key not in self._get_cached:
            self._get_cached[key] = dpath.util.get(self.data, list(path))
        return self._get_cached[key]

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


def process_input_func(data_to_process):
    (swagger, path, ref) = data_to_process
    sys.stdout.write('.')
    sys.stdout.flush()
    ref = ref.lstrip('#/').split('/')
    ref = tuple(ref)
    data = swagger.get(ref)
    path = path[:-1]
    return (path, RefNode(data, ref))


def process_references(swagger, pool):
    """
    Processed references in swagger data
    :param swagger:
    :return:
    """
    data_set = pool.map(process_input_func,
                        swagger.pickle_search(['**', '$ref']))
    for path, node in data_set:
        sys.stdout.write('.')
        sys.stdout.flush()
        next_ref = swagger.data
        for pn in path[:-1]:
            if isinstance(next_ref, list):
                next_ref = next_ref[int(pn)]
            elif isinstance(next_ref, dict):
                if pn in next_ref:
                    next_ref = next_ref[pn]
                elif int(pn) in next_ref:
                    next_ref = next_ref[int(pn)]
        if isinstance(next_ref, dict):
            idx = path[-1]
            next_ref[idx] = node
        elif isinstance(next_ref, list):
            idx = int(path[-1])
            next_ref[idx] = node
    print " "
