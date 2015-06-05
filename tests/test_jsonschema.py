from swagger_py_codegen.parser import Swagger
from swagger_py_codegen.jsonschema import build_data


def test_schema_base_01():
    data = {}
    swagger = Swagger(data)
    data = build_data(swagger)
    assert len(data['schemas']) == 0


def test_schema_base_02():
    data = {
        'definitions': {
            'Product': {
                'properties': {
                    'price': {'type': 'number'},
                    'name': {'type': 'string'},
                }
            }
        }
    }
    swagger = Swagger(data)
    data = build_data(swagger)
    assert len(data['schemas']) == 1


def test_schema_base_03():
    data = {
        'parameters': {
            "limitParam": {
                "name": "limit",
                "in": "query",
                "description": "max records to return",
                "required": True,
                "type": "integer",
                "format": "int32"
            }
        }
    }
    swagger = Swagger(data)
    data = build_data(swagger)
    assert len(data['schemas']) == 0


def test_schema_ref_01():
    data = {
        'definitions': {
            'Product': {
                'properties': {
                    'price': {'type': 'number'},
                    'name': {'type': 'string'},
                    'seller': {
                        '$ref': '#/definitions/User'
                    }
                }
            },
            'User': {
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'number'},
                }
            }
        }
    }
    swagger = Swagger(data)
    data = build_data(swagger)
    assert len(data['schemas']) == 2
    assert data['schemas'].keys()[0] == 'DefinitionsUser'


def test_validators():
    data = {
        'paths': {
            '/users': {
                'parameters': [
                    {'name': 'page', 'in': 'query', 'type': 'number', 'required': True},
                    {'name': 'limit', 'in': 'query', 'type': 'number'}
                ],
                'post': {
                    'parameters': [
                        {'name': 'user', 'in': 'body', 'schema': {'$ref': '#/definitions/User'}}
                    ]
                },
                'put': {
                    'parameters': [
                        {'name': 'user', 'in': 'body', 'schema': {
                            'properties': {
                                'id': {
                                    'type': 'number'
                                }
                            }
                        }}
                    ]
                }
            }
        },
        'definitions': {
            'Product': {
                'properties': {
                    'price': {'type': 'number'},
                    'name': {'type': 'string'},
                    'seller': {
                        '$ref': '#/definitions/User'
                    }
                }
            },
            'User': {
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'number'},
                }
            }
        }
    }
    swagger = Swagger(data)
    data = build_data(swagger)
    schemas = data['schemas']
    validators = data['validators']

    # body parameters
    assert ('/users', 'POST') in validators
    v1 = validators[('/users', 'POST')]['body']
    assert v1 == schemas['DefinitionsUser']

    # query parameters
    v2 = validators[('/users', 'POST')]['query']
    assert v2 == dict(
        required=['page'],
        properties=dict(
            page=dict(type='number'),
            limit=dict(type='number')))

    # no others parameters
    assert 'path' not in validators[('/users', 'POST')]

    # definitions
    assert 'DefinitionsUser' in schemas
    assert 'DefinitionsProduct' in schemas

    assert len(schemas) == 2


def test_filters():
    data = {
        'paths': {
            '/users': {
                'parameters': [
                    {'name': 'page', 'in': 'query', 'type': 'number', 'required': True},
                    {'name': 'limit', 'in': 'query', 'type': 'number'}
                ],
                'post': {
                    'parameters': [
                        {'name': 'user', 'in': 'body', 'schema': {'$ref': '#/definitions/User'}}
                    ],
                    'responses': {
                        '201': {
                            'schema': {'$ref': '#/definitions/User'},
                            'headers': {'X-COUNT': {'type': 'number'}},
                            'examples': {'application/json': {'id': 1, 'name': 'Bob', 'age': 12}}
                        },
                        '422': {
                            'schema': {
                                'properties': {
                                    'code': {'type': 'string'},
                                    'message': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        'definitions': {
            'Product': {
                'properties': {
                    'price': {'type': 'number'},
                    'name': {'type': 'string'},
                    'seller': {
                        '$ref': '#/definitions/User'
                    }
                }
            },
            'User': {
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'number'},
                }
            }
        }
    }
    swagger = Swagger(data)
    data = build_data(swagger)
    schemas = data['schemas']
    filters = data['filters']

    assert 201 in filters[('/users', 'POST')]
    assert 422 in filters[('/users', 'POST')]

    r1 = filters[('/users', 'POST')][201]
    r2 = filters[('/users', 'POST')][422]

    assert r1['schema'] == schemas['DefinitionsUser']
    assert r2['schema']['properties']['code'] == {'type': 'string'}


def test_object_to_dict():
    from swagger_py_codegen.jsonschema import object_to_dict

    class User:
        def __init__(self):
            self.id = 123
            self.name = 'somename'
            self.password = '****'
            self.address = object()

        @property
        def age(self):
            return 18

    schema = {
        'type': 'object',
        'properties': {
            'id': { 'type': 'integer' },
            'name': { 'type': 'string' },
            'gender': { 'type': 'string', 'default': 'unknown' },
            'address': {
                'type': 'object',
                'properties': {
                    'city': { 'type': 'string', 'default': 'beijing' },
                    'country': { 'type': 'string', 'default': 'china'}
                }
            },
            'age': { 'type': 'integer' },
            'roles': {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'default': 'user',
                    'enum': ['user', 'admin']
                }
            }
        }
    }

    user, errors = object_to_dict(schema, User())

    assert not errors
    assert 'password' not in user
    assert user['gender'] == 'unknown'
    assert user['address']['city'] == 'beijing'
    assert user['age'] == 18
    assert user['roles'] == ['user']
