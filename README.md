# Flask RESTful Application Code Generator


## Overview

Generate Flask-RESTful application code from a Swagger Specification doc.

**Alpha version for now, it can not handle all validation properly.**


## Requirements

This application requires Python version 2.7.   
This application requires the following libraries to be installed:
  * flask
  * PyYAML
  * click
  * jinja2
  * dpath


## Install

Using **pip**

    pip install swagger-py-codegen

or via sources:
    
    python setup.py install


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

Generate example-app from apis.yml:  

    $ mkdir example-app
    $tree
	.
	|__ api.yml
	|__ example-app 

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

    $ mkdir example-app
    $tree
	.
	|__ api.yml
	|__ example-app 

    $ swagger_py_codegen -s  api.yml  example-app-ui -p demo-ui --ui
    $ tree
	.
	|__ api.yml
	|__ example-app-ui
	   |__ demo-ui
	   |  |__ __init__.py
	   |  |__ static 
	   |  |  |__swagger-ui
	   |  |     |__ css
	   |  |     |  |__ print.css
	   |  |     |  |__ reset.css
	   |  |     |  |__ screen.css
	   |  |     |  |__ typography.css
	   |  |     |__ fonts
	   |  |     |  |__ droid-sans-v6-latin-700.eot
	   |  |     |  |__ droid-sans-v6-latin-700.svg
	   |  |     |  |__ droid-sans-v6-latin-700.ttf
	   |  |     |  |__ droid-sans-v6-latin-700.woff
	   |  |     |  |__ droid-sans-v6-latin-700.woff2
	   |  |     |  |__ droid-sans-v6-latin-regular.eot
	   |  |     |  |__ droid-sans-v6-latin-regular.svg
	   |  |     |  |__ droid-sans-v6-latin-regular.ttf
	   |  |     |  |__ droid-sans-v6-latin-regular.woff
	   |  |     |  |__ droid-sans-v6-latin-regular.woff2
	   |  |     |__ images
	   |  |     |  |__ explorer_icons.png
	   |  |     |  |__ favicon-16x16.png
	   |  |     |  |__ favicon-32x32.png
	   |  |     |  |__ favicon.ico
	   |  |     |  |__ logo_small.png
	   |  |     |  |__ pet_store_api.png
	   |  |     |  |__ throbber.gif
	   |  |     |  |__  wordnik_api.png
	   |  |     |__ index.html
	   |  |     |__ lib
	   |  |     |  |__ backbone-min.js
	   |  |     |  |__ handlebars-2.0.0.js
	   |  |     |  |__ highlight.7.3.pack.js
	   |  |     |  |__ jquery-1.8.0.min.js
	   |  |     |  |__ jquery.ba-bbq.min.js
	   |  |     |  |__ jquery.slideto.min.js
	   |  |     |  |__ jquery.wiggle.min.js
	   |  |     |  |__ marked.js
	   |  |     |  |__ swagger-oauth.js
	   |  |     |  |__ underscore-min.js
	   |  |     |  |__ underscore-min.map
	   |  |     |  |__ o2c.html
	   |  |     |__ swagger-ui.js
	   |  |     |__ swagger-ui.min.js
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

The example-app-ui follows are same with example-app.

## Authors
--------

* Rejown ( rejown@gmail.com )
* yimiqisan ( yimiqisan@gmail.com )
* softlns （softliunaisen@gmai.com )


## License
--------
MIT 

