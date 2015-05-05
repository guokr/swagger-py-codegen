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


