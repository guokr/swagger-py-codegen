# Python RESTful Web Framework Generator

[![Build Status][travis-image]][travis-url] [![PyPi Version][pypi-image]][pypi-url]

## Overview


Swagger Py Codegen is a Python web framework generator, which can help you generate a Python web framework automatically based on a given Swagger Specification doc. Currently, the following languages/frameworks are supported:


* [Flask](http://flask.pocoo.org/) (Python)
* [Tornado](http://www.tornadoweb.org/en/stable/) (Python)
* [Falcon](https://falconframework.org/) (Python)
* [Sanic](https://github.com/channelcat/sanic) (Python)


**Alpha version for now, it may not handle all validation properly. If you found a bug, feel free to contact us.**


## Install

```
pip install swagger-py-codegen
```

## Usage

Create all:

```
swagger_py_codegen --swagger-doc api.yml example-app
```

Command Options:

	-s, --swagger-doc               Swagger doc file.  [required]
	-f, --force                     Force overwrite.
	-p, --package                   Package name / application name.
	-t, --template-dir              Path of your custom templates directory.
	--spec, --specification         Generate online specification json response.
	--ui                            Generate swagger ui.
	--validate                      Validate swagger file.
	-tlp, --templates               gen flask/tornado/falcon templates, default flask.
	--version                       Show current version.
	--help                          Show this message and exit.

## Examples:

Generate example-app from [api.yml](https://github.com/guokr/swagger-py-codegen/blob/master/api.yml "Title"):

#### Flask Example

    $ swagger_py_codegen -s api.yml example-app -p demo
    $ tree (flask-demo)
	.
	|__ api.yml
	|__ example-app
	   |__ demo
	   |  |__ __init__.py
	   |  |__ v1
	   |     |__ api
	   |     |  |__ __init__.py
	   |     |  |__ pets.py
	   |     |  |__ pets_petId.py
	   |     |__ __init__.py
	   |     |__ routes.py
	   |     |__ schemas.py
	   |     |__ validators.py
	   |__ requirements.txt

#### Tornado Example

	$ swagger_py_codegen -s api.yml example-app -p demo -tlp=tornado
    $ tree (tornado-demo)
	.
	|__ api.yml
	|__ example-app
	   |__ demo
	   |  |__ __init__.py
	   |  |__ core
	   |     |__ __init.py
	   |  |__ v1
	   |     |__ api
	   |     |  |__ __init__.py
	   |     |  |__ pets.py
	   |     |  |__ pets_petId.py
	   |     |__ __init__.py
	   |     |__ routes.py
	   |     |__ schemas.py
	   |     |__ validators.py
	   |__ requirements.txt

#### Falcon Example

    $ swagger_py_codegen -s api.yml example-app -p demo -tlp=falcon
    $ tree (falcon-demo)
	.
	|__ api.yml
	|__ example-app
	   |__ demo
	   |  |__ __init__.py
	   |  |__ v1
	   |     |__ api
	   |     |  |__ __init__.py
	   |     |  |__ pets.py
	   |     |  |__ pets_petId.py
	   |     |__ __init__.py
	   |     |__ routes.py
	   |     |__ schemas.py
	   |     |__ validators.py
	   |__ requirements.txt


#### Sanic Example

    $ swagger_py_codegen -s api.yml example-app -p demo -tlp=sanic
    $ tree (sanic-demo)
	.
	|__ api.yml
	|__ example-app
	   |__ demo
	   |  |__ __init__.py
	   |  |__ v1
	   |     |__ api
	   |     |  |__ __init__.py
	   |     |  |__ pets.py
	   |     |  |__ pets_petId.py
	   |     |__ __init__.py
	   |     |__ routes.py
	   |     |__ schemas.py
	   |     |__ validators.py
	   |__ requirements.txt


#### Run Web Server

Install example-app requirements:

    $ cd example-app
    $ pip install -r requirements.txt

Start example-app:

    $ cd demo
    $ python __init__.py

And generate example-app-ui from api.yml with ui:

    $ swagger_py_codegen -s api.yml  example-app-ui -p demo-ui --ui --spec

Then you can visit [http://127.0.0.1:5000/static/swagger-ui/index.html](http://127.0.0.1:5000/static/swagger-ui/index.html) in a browser.


#### OAuth2 Scopes Usage

See the [wiki](https://github.com/guokr/swagger-py-codegen/wiki/OAuth2-Scopes-Usage)


## Compatibility

|component|compatibility|
|-----|-----|
|OpenAPI Spec|2.0|
|Python|2.\*, 3.\*(Sanic only 3.\*)|


## Authors

See the [AUTHORS](https://github.com/guokr/swagger-py-codegen/blob/master/AUTHORS "Title").


## License

MIT

[travis-url]: https://travis-ci.org/guokr/swagger-py-codegen
[travis-image]: https://travis-ci.org/guokr/swagger-py-codegen.svg

[pypi-url]: https://pypi.python.org/pypi/swagger-py-codegen/
[pypi-image]: https://img.shields.io/pypi/v/swagger-py-codegen.svg?style=flat-square
