from __future__ import absolute_import
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
    assert list(data['schemas'].keys())[0] == 'DefinitionsUser'


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


def test_build_default_01():
    from swagger_py_codegen.jsonschema import build_default

    schema = {
        'required': ['id', 'name', 'gender', 'roles'],
        'type': 'object',
        'properties': {
            'id': { 'type': 'integer' },
            'name': { 'type': 'string' },
            'gender': { 'type': 'string', 'default': 'unknown' },
            'address': {
                'type': 'object',
                'properties': {
                    'city': { 'type': 'string' },
                    'country': { 'type': 'string' }
                },
                'default': { 'city':'beijing', 'country':'china' }
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
    result = build_default(schema)
    assert result['gender'] == 'unknown'
    assert result['address']['city'] == 'beijing'
    assert result['roles'] == []


def test_merge_default_01():
    from swagger_py_codegen.jsonschema import merge_default

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
    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen'
        },
        'roles': ['admin', 'user']
    }
    result = merge_default(schema, default)
    assert result['id'] == 123
    assert result['name'] == 'bob'
    assert result['address'] == {'city': 'shenzhen', 'country': 'china'}
    assert result['roles'] == ['admin', 'user']

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen'
        }
    }
    result = merge_default(schema, default)
    assert 'roles' not in list(result.keys())


def test_merge_default_02():
    from swagger_py_codegen.jsonschema import merge_default

    schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'string',
                    'default': 'Tom'
                }
            }
        }
    }

    default = [{
        'id': 123,
    }, {
        'name': 'Jerry'
    }]

    results = merge_default(schema, default)
    assert results[0]['name'] == 'Tom'
    assert results[1]['name'] == 'Jerry'


def test_merge_default_03():
    from swagger_py_codegen.jsonschema import merge_default

    schema = {
        'type': 'array',
        'items': {
                'type': 'object',
                'properties': {
                    'city': { 'type': 'string', 'default': 'beijing' },
                    'country': { 'type': 'string', 'default': 'china'}
                }
        }
    }
    result = merge_default(schema, [{}])
    assert result[0]['city'] == 'beijing'
    assert result[0]['country'] == 'china'


def test_normalize_01():
    from swagger_py_codegen.jsonschema import normalize

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
        'required': ['id', 'name', 'gender', 'roles'],
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
                },
                'default': ['user']
            }
        }
    }

    user, errors = normalize(schema, User())

    assert not errors
    assert 'password' not in user
    assert user['gender'] == 'unknown'
    assert user['address']['city'] == 'beijing'
    assert user['age'] == 18
    assert user['roles'] == ['user']

    schema = {
        'type': 'array',
        'items': schema
    }
    users, errors = normalize(schema, [User()])
    user = users.pop()
    assert not errors
    assert 'password' not in user
    assert user['gender'] == 'unknown'
    assert user['address']['city'] == 'beijing'
    assert user['age'] == 18
    assert user['roles'] == ['user']

    del schema['items']['properties']['roles']['default']
    users, errors = normalize(schema, [User()])
    user = users.pop()
    assert 'roles' not in list(user.keys())
    assert errors

    user = User()
    user.roles = ['admin']
    results, errors = normalize(schema, [user])
    result = results.pop()
    assert result['roles'] == ['admin']


def test_normalize_02():
    from swagger_py_codegen.jsonschema import normalize

    schema = {
        'required': ['id', 'name', 'gender', 'roles'],
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
    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen'
        },
        'roles': ['admin', 'user']
    }
    result, errors = normalize(schema, default)
    assert result['id'] == 123
    assert result['name'] == 'bob'
    assert result['address'] == {'city': 'shenzhen', 'country': 'china'}
    assert result['roles'] == ['admin', 'user']

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen'
        }
    }
    result, errors = normalize(schema, default)
    assert 'roles' not in list(result.keys())
    assert errors


def test_normalize_03():
    from swagger_py_codegen.jsonschema import normalize

    schema = {
        'required': ['id', 'name', 'gender'],
        'type': 'object',
        'properties': {
            'id': { 'type': 'integer' },
            'name': { 'type': 'string' },
            'gender': { 'type': 'string', 'default': 'unknown' },
            'address': {
                'required': ['city', 'country'],
                'type': 'object',
                'properties': {
                    'city': { 'type': 'string' },
                    'country': { 'type': 'string'}
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
    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'roles': ['admin', 'user']
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['name'] == 'bob'
    assert 'address' not in list(result.keys())

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen',
            'country': 'china'
        }
    }
    result, errors = normalize(schema, default)
    assert result['address'] == {'city': 'shenzhen', 'country': 'china'}

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'beijing'
        }
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 1
    assert result['address'] == {'city': 'beijing'}

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {}
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 2


def test_normalize_04():
    from swagger_py_codegen.jsonschema import normalize

    schema = {
        'required': ['id', 'name', 'gender', 'address'],
        'type': 'object',
        'properties': {
            'id': { 'type': 'integer' },
            'name': { 'type': 'string' },
            'gender': { 'type': 'string', 'default': 'unknown' },
            'address': {
                'required': ['city', 'country'],
                'type': 'object',
                'properties': {
                    'city': { 'type': 'string' },
                    'country': { 'type': 'string'}
                },
                'default': {'city': 'beijing', 'country': 'china'}
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
    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'roles': ['admin', 'user']
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['address'] == {'country': 'china', 'city': 'beijing'}

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {
            'city': 'shenzhen',
        }
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 1
    assert result['address'] == {'city': 'shenzhen'}

    default = {
        'id': 123,
        'name': 'bob',
        'gender': 'male',
        'address': {}
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 2


def test_normalize_05():
    from swagger_py_codegen.jsonschema import normalize
    class Pet(object):
        def __init__(self, name, petType):
            self.name = name
            self.petType = petType

    class Cat(Pet):
        def __init__(self, huntingSkill, **kwargs):
            if kwargs:
                super(Cat, self).__init__(**kwargs)
            self.huntingSkill = huntingSkill

    schema = {
        'description': 'A representation of a cat',
        'allOf': [
            {
                'discriminator': 'petType',
                'required': ['name', 'petType'],
                'type': 'object',
                'properties': {
                    'petType': {'type': 'string'},
                    'name': {'type': 'string'}
                }
            },
            {
                'required': ['huntingSkill'],
                'type': 'object',
                'properties': {
                    'huntingSkill': {
                        'default': 'lazy',
                        'enum': ['clueless', 'lazy', 'adventurous', 'aggressive'],
                        'type': 'string',
                        'description': 'The measured skill for hunting'
                    }
                }
            }
        ]
    }

    result, errors = normalize(schema, Cat(huntingSkill='lazy', name='bob', petType='cat'))
    assert errors == []
    assert result['name'] == 'bob'
    assert result['petType'] == 'cat'
    assert result['huntingSkill'] == 'lazy'

    result, errors = normalize(schema, Cat(huntingSkill='lazy'))
    assert result['huntingSkill'] == 'lazy'
    assert errors
    assert len(errors) == 2


def test_normalize_06():
    from swagger_py_codegen.jsonschema import normalize

    schema = {
        'description': 'A representation of a cat',
        'allOf': [
            {
                'discriminator': 'petType',
                'required': ['name', 'petType'],
                'type': 'object',
                'properties': {
                    'petType': {'type': 'string'},
                    'name': {'type': 'string'}
                }
            },
            {
                'required': ['huntingSkill'],
                'type': 'object',
                'properties': {
                    'huntingSkill': {
                        'default': 'lazy',
                        'enum': ['clueless', 'lazy', 'adventurous', 'aggressive'],
                        'type': 'string',
                        'description': 'The measured skill for hunting'
                    }
                }
            }
        ]
    }
    default = {
        'name': 'bob',
        'petType': 'cat',
        'huntingSkill': 'lazy'
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['name'] == 'bob'
    assert result['petType'] == 'cat'
    assert result['huntingSkill'] == 'lazy'

    default = {
        'name': 'bob',
        'petType': 'cat',
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['name'] == 'bob'
    assert result['petType'] == 'cat'
    assert result['huntingSkill'] == 'lazy'

    default = {
        'name': 'bob',
        'huntingSkill': 'lazy'
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 1
    assert result['huntingSkill'] == 'lazy'

    default = {
        'huntingSkill': 'lazy'
    }
    result, errors = normalize(schema, default)
    assert errors
    assert len(errors) == 2
    assert result['huntingSkill'] == 'lazy'


def test_normalize_07():
    from swagger_py_codegen.jsonschema import normalize

    class A(object):
        def __init__(self, visible_property):
            self.visible_property = visible_property

    schema = {
        'additionalProperties': {'type': 'string'},
        'discriminator': 'response info',
        'type': 'object',
        'properties': {
            'visible_property': {
                'type': 'string',
                'description': 'This is a property that you can see'
            }
        }
    }

    data = A(visible_property='the property you see')
    data.additional_property1 = 'test1'
    data.additional_property2 = 'test2'
    result, errors = normalize(schema, data)
    assert errors == []
    assert result['visible_property'] == 'the property you see'
    assert result['additional_property1'] == 'test1'
    assert result['additional_property2'] == 'test2'

    default = {
        'visible_property': 'default visible property',
        'additional_property01': 'test01',
        'additional_property02': 'test02',
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['visible_property'] == 'default visible property'
    assert result['additional_property01'] == 'test01'
    assert result['additional_property02'] == 'test02'


def test_normalize_08():
    from swagger_py_codegen.jsonschema import normalize

    class A(object):
        def __init__(self, visible_property):
            self.visible_property = visible_property

    class B(object):
        def __init__(self, subobject):
            self.subobject = subobject

    schema = {
        'additionalProperties': {
            'required': ['subobject'],
            'properties': {
                'subobject': {
                    'type': 'string',
                    'description': 'Some string value'
                }
            }
        },
        'discriminator': 'response info',
        'type': 'object',
        'properties': {
            'visible_property': {
                'type': 'string',
                'description': 'This is a property that you can see'
            }
        }
    }

    data = A(visible_property='default property')
    data.additional_property1 = B('test1')
    data.additional_property2 = B('test2')
    result, errors = normalize(schema, data)
    assert errors == []
    assert result['visible_property'] == 'default property'
    assert result['additional_property1'] == {'subobject': 'test1'}
    assert result['additional_property2'] == {'subobject': 'test2'}

    default = {
        'visible_property': 'default visible property',
        'additional_property01': {'subobject': 'test01'},
        'additional_property02': {},
    }
    result, errors = normalize(schema, default)
    assert len(errors) == 1
    assert result['visible_property'] == 'default visible property'
    assert result['additional_property01'] == {'subobject': 'test01'}

    default = {
        'visible_property': 'default visible property',
        'additional_property01': {'subobject': 'test01'},
        'additional_property02': {'subobject': 'test02'},
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['visible_property'] == 'default visible property'
    assert result['additional_property01'] == {'subobject': 'test01'}
    assert result['additional_property02'] == {'subobject': 'test02'}


def test_normalize_09():
    from swagger_py_codegen.jsonschema import normalize

    class A(object):
        def __init__(self, visible_property):
            self.visible_property = visible_property

    schema = {
        'additionalProperties': {},
        'discriminator': 'response info',
        'type': 'object',
        'properties': {
            'visible_property': {
                'type': 'string',
                'description': 'This is a property that you can see'
            },
            'aps': {
                'additionalProperties': True,
            }
        }
    }

    data = A(visible_property='the property you see')
    data.aps = A('aps')
    data.additional_property1 = 'string'
    data.additional_property2 = 123
    data.aps.additional_property1 = 'aps.string'
    data.aps.additional_property2 = 1234
    result, errors = normalize(schema, data)
    assert errors == []
    assert result['visible_property'] == 'the property you see'
    assert result['additional_property1'] == 'string'
    assert result['additional_property2'] == 123
    assert result['aps']['additional_property1'] == 'aps.string'
    assert result['aps']['additional_property2'] == 1234

    default = {
        'visible_property': 'default visible property',
        'additional_property01': 'test01',
        'additional_property02': 123,
        'aps': {
            'additional_property01': 'aps.test01',
            'additional_property02': 1234,
        }
    }
    result, errors = normalize(schema, default)
    assert errors == []
    assert result['visible_property'] == 'default visible property'
    assert result['additional_property01'] == 'test01'
    assert result['additional_property02'] == 123
    assert result['aps']['additional_property01'] == 'aps.test01'
    assert result['aps']['additional_property02'] == 1234
