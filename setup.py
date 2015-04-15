import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('flask_swagger_codegen/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='Flask-Swagger-Codegen',
    description='Generate Flask code from Swagger docs.',
    version=version,
    author='Rejown',
    author_email='rejown@gmail.com',
    url='http://github.com/rejown/flask-swagger-codegen',
    packages=['flask_swagger_codegen'],
    package_data={'flask_swagger_codegen': ['templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'flask_swagger_codegen=flask_swagger_codegen:codegen'
        ]
    },
    install_requires=['click', 'jinja2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
