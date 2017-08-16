from __future__ import absolute_import
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('swagger_py_codegen/_version.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

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
    install_requires=requirements,
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
)
