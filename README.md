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

## TEST

The unit tests are contained in the tests/ directory (which is a Python package).  
To run all the tests manually use py.test command:

    $ py.test


## Authors
--------

* Rejown ( rejown@gmail.com )


## License
--------
MIT 
