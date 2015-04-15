# -*- coding: utf-8 -*-
import pytest
from flask_swagger_codegen import parser, model, generator
from flask_swagger_codegen.resolver import FlaskModelResolver

import yaml
import codecs

@pytest.fixture
def swagger_data():
    with codecs.open('tests/swagger_specs/oauth.yml', 'r', 'utf-8') as f:
        swagger = parser.SwaggerParser().parse_yaml(f)
    return swagger

@pytest.fixture
def m(swagger_data):
    return FlaskModelResolver(swagger_data).resolve()

def test_swagger_parser_definitions_ref():
    yml = '''a:
  a1:
    - $ref: '#/definitions/C'
definitions:
  A:
    $ref: '#/definitions/B'
  B:
    properties:
      user_name:
        type: string
        description: user name
  C:
    properties:
      password:
        type: string
        description: user pass
'''
    swagger = parser.SwaggerParser().parse_yaml(yml)
    assert swagger['definitions']['A'] == swagger['definitions']['B']
    assert swagger['a']['a1'][0] == swagger['definitions']['C']


def test_model(m):
    p = m
    assert 'Authentication' in p.schemas
    assert 'OauthAuthApproachApproach' in p.resources
    assert 'DELETE' in p.resources['OauthAuthApproachApproach'].methods
    assert 'headers' in p.resources['OauthAuthApproachApproach'].methods['DELETE'].request_location_schemas
    assert ('oauth_auth_approach_approach', 'DELETE', 'headers') in p.validators
    found = False
    for route in p.routes:
        if '/oauth/auth_approach/<approach>' in route['urls']:
            found = True
            break
    assert found is True


def test_generate_routes(m):
    g = generator.Generator(m)

    expect_line = "{'endpoint': 'oauth_auth_approach_approach', 'resource': OauthAuthApproachApproach, 'urls': ['/oauth/auth_approach/<approach>']},"
    found = False
    for line in g.generate_routes().splitlines():
        if expect_line in line:
            found = True
    assert found is True


def test_generate_schemas(m):
    g = generator.Generator(m)

    expect_line = "scope = fields.List(cls_or_instance=fields.Enum(choices=['register', 'open']))"
    found = False
    for line in g.generate_schemas().splitlines():
        if expect_line in line:
            found = True
    assert found is True


def test_generate_validators(m):
    g = generator.Generator(m)

    expect_line = "('oauth_auth_approach', 'POST', 'headers'): schemas.OauthAuthApproachPOSTHeadersSchema,"
    found = False
    for line in g.generate_validators().splitlines():
        if expect_line in line:
            found = True
    assert found is True


def test_generate_views(m):
    g = generator.Generator(m)

    expect_line = 'def delete(self, approach):'
    found = False
    for v, t in  g.generate_views():
        for line in t.splitlines():
            if expect_line in line:
                found = True
    assert found is True
