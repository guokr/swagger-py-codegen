# -*- coding: utf-8 -*-

import pytest

from swagger_py_codegen import model


def test_method_response_default_values_01():
    method = model.Method('get', None)

    schema = model.Schema('User')
    schema.add_field('nick', model.Field('string', kwargs=dict(default='hehe')))
    schema.add_field('gender', model.Field('Enum', kwargs=dict(choices=['male', 'female'])))

    # return simple object with default values
    method.response_filter = model.ResponseFilter(200, schema, False)
    assert method.response == dict(nick='hehe', gender='male'), 'method response value is not expected.'

    # return list of simple object, if many is True
    method.response_filter = model.ResponseFilter(200, schema, True)
    assert method.response == [dict(nick='hehe', gender='male')], 'method response value is not expected.'

    # return example object, if response_example is provided
    method.response_example = dict(a=dict(aa='AA', bb='BB'), b='B')
    assert method.response == method.response_example, 'method response value is not expected.'

    # return headers, if headers is provided
    method.headers = [('a', 'A'), ('b', 'B')]
    assert method.response == (method.response_example, 200, method.headers), 'method response value is not expected.'


def test_model_supported_scope_set():
    m = model.SwaggerFlaskModel()
    resource_a = model.Resource('/a', m)

    method_a = model.Method('get', resource_a)
    method_a.scopes = ['scope_a', 'scope_b']
    method_b = model.Method('post', resource_a)
    method_b.scopes = ['scope_b', 'scope_c']

    resource_a.methods = {'a': method_a, 'b': method_b}

    m.add_resource(resource_a)
    assert m.supported_scope_set == set(['scope_a', 'scope_b', 'scope_c'])

