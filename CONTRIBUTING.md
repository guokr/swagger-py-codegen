# Contributing

Welcome to contribute! We are following the next standards.

## Installation

Use `virtualenv` create the develop environment:

```
cd swagger-py-codegen
virtualenv .
source bin/activate
pip install -r requirements.txt
```

## Running tests

Use `tox` to run the tests:

```
tox
```

If `tox` not installed:
```
pip install -U tox
```

## Maybe give it a try

After all these done, just have a try to see if everything goes as expected:

```
python setup.py install
swagger_py_codegen -s api.yml example-app -p demo
```
