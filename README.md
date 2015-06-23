# Flask RESTful Application Code Generator

[![Build Status](https://travis-ci.org/guokr/swagger-py-codegen.svg)](https://travis-ci.org/guokr/swagger-py-codegen)

## Overview

Generate Flask-RESTful application code from a Swagger Specification doc.

**Alpha version for now, it can not handle all validation properly.**


## Install

```
pip install swagger-py-codegen
```

## Usage

Create all:

```
swagger-py-codegen --swagger-doc api.yml example-app
```

Command Options:

    -s, --swagger, --swagger-doc        Swagger doc file.  [required]
    -f, --force                         Force overwrite.
    -p, --package                       Package name / application name.
    -t, --template-dir                  Path of your custom templates directory.
    --spec, --specification             Generate online specification json response.
    --ui                                Generate swagger ui.
    --help                              Show this message and exit.

## Examples:

Generate example-app from [apis.yml](https://github.com/guokr/swagger-py-codegen/blob/master/api.yml "Title"):  

    $tree
	.
	|__ api.yml

    $ swagger_py_codegen -s  api.yml  example-app -p demo
    $ tree
	.
	|__ api.yml
	|__ example-app
	   |__ demo
	   |  |__ __init__.py
	   |  |__ v1
	   |     |__ api
	   |     |  |__ __init__.py
	   |     |  |__ oauth_auth_approach_approach.py
	   |     |  |__ oauth_auth_approach.py
	   |     |  |__ users_token.py
	   |     |  |__ users_current.py
	   |     |  |__ users.py
	   |     |__ __init__.py
	   |     |__ routes.py
	   |     |__ schemas.py
	   |     |__ validators.py
	   |__ requirements.txt
	
Install example-app requirements: 

    $ cd example-app
    $ pip install -r requirements.txt

Start example-app: 

    $ cd demo
    $ python __init__.py

And generate example-app-ui from apis.yml with ui:   

    $ swagger_py_codegen -s  api.yml  example-app-ui -p demo-ui --ui

## Authors
--------
See the [AUTHORS](https://github.com/guokr/swagger-py-codegen/blob/master/AUTHORS "Title").


## License
--------
MIT 
