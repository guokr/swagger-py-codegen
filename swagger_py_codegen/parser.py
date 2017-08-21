# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import copy
import six
from six.moves import map

import dpath.util
from jsonspec.reference import resolve


def schema_var_name(path):
    return ''.join(map(str.capitalize, path))


class RefNode(dict):

    def __init__(self, data, ref):
        self.ref = ref
        super(RefNode, self).__init__(data)

    def __repr__(self):
        return schema_var_name(self.ref)


class SwaggerSpecError(Exception):
    pass


class Swagger(object):

    separator = '\0'

    def __init__(self, data, pool=None):
        self.data = data
        self.origin_data = copy.deepcopy(data)
        self._definitions = []
        self._resolve_definitions()
        self._get_cached = {}
        if pool:
            pool.map()
            process_references(self, pool)
        else:
            self._process_ref()

    def _process_ref(self):
        """
        resolve all references util no reference
        """
        while 1:
            li = self.search(['**', '$ref'])
            if not li:
                break
            for path, ref in li:
                data = resolve(self.data, ref)
                path = path[:-1]
                self.set(path, data)

    def _resolve_definitions(self):
        """
        ensure there not exists circular references and load definitions
        """

        def get_definition_refs():
            definition_refs_default = {}
            definition_refs = {}
            for path, _ in self.search(['definitions', '*']):
                definition_refs_default[path] = set([])
            for path, ref in self.search(['definitions', '**', '$ref']):
                schema = tuple(path[0:2])
                ref = ref.lstrip('#/').split('/')
                ref = tuple(ref)

                if schema in list(definition_refs.keys()):
                    definition_refs[schema].add(ref)
                else:
                    definition_refs[schema] = set([ref])

            definition_refs_default.update(definition_refs)
            return definition_refs_default

        definition_refs = get_definition_refs()
        while definition_refs:
            ready = {definition for definition, refs in six.iteritems(definition_refs) if not refs}
            if not ready:
                msg = '$ref circular references found!\n'
                raise ValueError(msg)
            for definition in ready:
                del definition_refs[definition]
            for refs in six.itervalues(definition_refs):
                refs.difference_update(ready)

            self._definitions += ready

    def search(self, path):
        li = []
        for p, d in dpath.util.search(self.data, list(path), True, self.separator):
            li.append((tuple(p.split(self.separator)), d))
        return li

    def pickle_search(self, path):
        for p, d in dpath.util.search(self.data, list(path), True,
                                      self.separator):
            yield (self, tuple(p.split(self.separator)), d)

    def get(self, path):
        key = ''.join(path)
        if key not in self._get_cached:
            value = self.data
            for p in path:
                value = value[p]
            self._get_cached[key] = value
        return self._get_cached[key]

    def set(self, path, data):
        dpath.util.set(self.data, list(path), data)

    @property
    def definitions(self):
        return self._definitions

    @property
    def scopes_supported(self):
        for _, data in self.search(['securityDefinitions', '*', 'scopes']):
            return list(data.keys())
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
    try:
        data = swagger.get(ref)
    except KeyError:
        raise SwaggerSpecError('%s %s not defined' % ref)
    # data = resolve(swagger.data, ref)
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
