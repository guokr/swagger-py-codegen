from swagger_py_codegen.parser import Swagger


def test_swagger_ref_count_01():
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
    assert swagger.definitions[0] == ('definitions', 'User')


def test_swagger_ref_count_02():
    data = {
        'definitions': {
            'Order': {
                'properties': {
                    'customer': {
                        '$ref': '#/definitions/User'
                    },
                    'seller': {
                        '$ref': '#/definitions/User'
                    },
                    'products': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/definitions/Product'
                        }
                    }
                }
            },
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
    assert swagger.definitions[0] == ('definitions', 'User')
    assert swagger.definitions[1] == ('definitions', 'Product')
    assert swagger.definitions[2] == ('definitions', 'Order')


def test_swagger_ref_node():
    data = {
        'definitions': {
            'Order': {
                'properties': {
                    'customer': {
                        '$ref': '#/definitions/User'
                    },
                    'seller': {
                        '$ref': '#/definitions/User'
                    },
                    'products': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/definitions/Product'
                        }
                    }
                }
            },
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
    p = swagger.get(['definitions', 'Order', 'properties', 'products', 'items'])
    assert p['properties']['name']['type'] == 'string'
    assert str(p) == 'DefinitionsProduct'
    assert repr(p) == 'DefinitionsProduct'
