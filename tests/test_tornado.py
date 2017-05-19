from __future__ import absolute_import

from swagger_py_codegen.parser import Swagger
from swagger_py_codegen.tornado import (
    _swagger_to_tornado_url,
    _path_to_endpoint,
    _path_to_resource_name,
    TornadoGenerator
)

def test_swagger_to_tornado_url():
    cases = [
        {
            'url': '/users/{id}',
            'data': {
                'parameters': [{
                    'name': 'id',
                    'in': 'path',
                    'type': 'integer'
                }],
                'get': {
                    'parameters': [{
                        'name': 'limit',
                        'in': 'query',
                        'type': 'integer'
                    }]
                },
                'post': {
                    'parameters': [{
                        'name': 'user',
                        'in': 'body',
                        'schema': {
                            'properties': {
                                'name': {'type': 'string'}
                            }
                        }
                    }]
                }
            },
            'expect': (
                '/users/<int:id>',
                ['id']
            )
        },
        {
            'url': '/goods/categories/{category}/price-large-than/{price}/order-by/{order}',
            'data': {
                'get': {
                    'parameters': [{
                        'name': 'limit',
                        'in': 'query',
                        'type': 'integer'
                    }, {
                        'name': 'order',
                        'in': 'path',
                        'type': 'string'
                    }, {
                        'name': 'price',
                        'in': 'path',
                        'type': 'float'
                    }]
                },
                'parameters': [{
                    'name': 'category',
                    'in': 'path',
                    'type': 'integer'
                }]
            },
            'expect': (
                '/goods/categories/<int:category>/price-large-than/<float:price>/order-by/<order>',
                ['category', 'price', 'order']
            )
        },
        {
            'url': '/products/{product_id}',
            'data': {},
            'expect': (
                '/products/<product_id>',
                ['product_id']
            )
        }
    ]
    for case in cases:
        assert _swagger_to_tornado_url(case['url'], case['data']) == case['expect']


def test_path_to_endpoint():
    cases = [{
        'path': '/users/{id}',
        'expect': 'users_id'
    }, {
        'path': '/users/{id}/profile',
        'expect': 'users_id_profile'
    }, {
        'path': '/users/{id}/hat-size',
        'expect': 'users_id_hat_size'
    }]
    for case in cases:
        assert _path_to_endpoint(case['path']) == case['expect']


def test_path_to_resource_name():
    cases = [{
        'path': '/users/{id}',
        'expect': 'UsersId'
    }, {
        'path': '/users/{id}/profile',
        'expect': 'UsersIdProfile'
    }, {
        'path': '/posts/{post_id}/last-reply',
        'expect': 'PostsPostIdLastReply'
    }]
    for case in cases:
        assert _path_to_resource_name(case['path']) == case['expect']


def test_process_data():
    data = {
        'paths': {
            '/users': {
                'get': {},
                'put': {},
                'head': {},
                'parameters': []
            },
            '/posts/{post_id}': {
                'get': {
                    'parameters': [
                        {'name': 'post_id', 'in': 'path', 'type': 'integer'},
                        {'name': 'page', 'in': 'query', 'type': 'integer'}
                    ]
                }
            }
        }
    }
    swagger = Swagger(data)
    generator = TornadoGenerator(swagger)
    schemas, routes, view1, view2 = list(generator.generate())[:4]
    view1, view2 = sorted([view1, view2], key=lambda x: x.data['name'])
    assert ('posts_post_id', 'GET') in schemas.data['validators']
    assert schemas.data['validators'][('posts_post_id', 'GET')]['args']['properties']['page']['type'] == 'integer'
    assert view1.data['url'] == '/posts/(?P<post_id>[^/]+?)'
    assert view1.data['name'] == 'PostsPostId'
