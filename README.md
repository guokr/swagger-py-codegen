# Flask RESTful Application Code Generator

[![Build Status](https://travis-ci.org/softlns/swagger-py-codegen.svg)](https://travis-ci.org/softlns/swagger-py-codegen)

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

## TODO

- validation support
- generate client
- generate tests
