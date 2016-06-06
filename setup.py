import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('swagger_py_codegen/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='swagger-py-codegen',
    description='Generate Flask code from Swagger docs.',
    version=version,
    author='Rejown',
    author_email='rejown@gmail.com',
    url='http://github.com/guokr/swagger-py-codegen',
    packages=['swagger_py_codegen'],
    package_data={'templates': ['swagger_py_codegen/templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'swagger_py_codegen=swagger_py_codegen:generate'
        ]
    },
    install_requires=['PyYAML', 'click', 'jinja2', 'dpath'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
