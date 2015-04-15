# Flask RESTful Application Code Generator

## Overview

Generate Flask-RESTful application code from a Swagger Specification doc.

**Alpha version for now, it can not handle all validation properly.** 

## Install

```
pip install Flask-Swagger-Codegen
```

## Usage

Create all:

```
flask-swagger-codegen --swagger-doc api.yml example-app
```

## TODO

- validation support
- generate client
- generate tests
