from __future__ import absolute_import
from os import path, listdir
import codecs

from swagger_py_codegen.jsonschema import Schema

try:
    import simplejson as json
except ImportError:
    import json
from os import makedirs
from os.path import join, exists, dirname, isdir

import six
import yaml
import click

from swagger_spec_validator import SwaggerValidationError
from swagger_spec_validator.validator20 import validate_spec

from ._version import __version__
from .flask import FlaskGenerator
from .tornado import TornadoGenerator
from .falcon import FalconGenerator
from .sanic import SanicGenerator
from .parser import Swagger
from .base import Template


def get_ref_filepath(filename, ref_file):
    ref_file = path.normpath(path.join(path.dirname(filename), ref_file))
    return ref_file


def get_loader(filename):
    if filename.endswith('.json'):
        loader = json.load
    elif filename.endswith('.yml') or filename.endswith('.yaml'):
        loader = yaml.load
    else:
        with codecs.open(filename, 'r', 'utf-8') as f:
            contents = f.read()
            contents = contents.strip()
            if contents[0] in ['{', '[']:
                loader = json.load
            else:
                loader = yaml.load
    return loader


def load_file(filename, spec_data):
    loader = get_loader(filename)
    with codecs.open(filename, 'r', 'utf-8') as f:
        data = loader(f)
        # modify_spec_data(spec_data, data)
        spec_data.update(data)
        for field, values in six.iteritems(data):
            if field not in ['definitions', 'parameters', 'paths']:
                continue
            if not isinstance(values, dict):
                continue
            for _field, value in six.iteritems(values):
                # _field is the endpoint for paths when the api of paths contains $ref
                if _field == '$ref' and value.endswith('.yml'):
                    _filepath = get_ref_filepath(filename, value)
                    field_data = spec_load(_filepath)
                    # modify_spec_data(field, spec_data, field_data)
                    spec_data[field] = field_data
                elif '$ref' in value:
                    v = value.pop('$ref', '')
                    if not v:
                        continue
                    _filepath = get_ref_filepath(filename, v)
                    field_data = spec_load(_filepath)
                    modify_spec_data(field, spec_data, field_data)
                    # spec_data[field][_field] = field_data.values()


def dump_file(filename, data):
    if not filename.endswith('.yml'):
        return None
    if not exists(filename):
        dirs = filename.rsplit('/', 1)[0]
        # dirs, fn = '/'.join(paths[:-1]), paths[-1]
        if not exists(dirs):
            makedirs(dirs)
    with codecs.open(filename, 'w', 'utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def modify_spec_data(field, spec_data, data):
    if not isinstance(spec_data, dict) or not isinstance(data, dict):
        return None
    for k, v in data.items():
        if k in spec_data[field]:
            spec_data[field][k].update(v)
        else:
            spec_data[field][k] = v


def spec_load(filename):
    spec_data = {}
    files = listdir(filename) if isdir(filename) else [filename]
    for f in files:
        if f != filename:
            f = filename + '/' + f
        load_file(f, spec_data)
    return spec_data


def write(dist, content):
    dir_ = dirname(dist)
    if not exists(dir_):
        makedirs(dir_)
    with codecs.open(dist, 'w', 'utf-8') as f:
        f.write(content)


def _copy_ui_dir(ui_dest, ui_src):
    from distutils.dir_util import copy_tree
    from os import unlink

    if exists(ui_dest):
        status = 'skip'
    else:
        status = 'generate'
        makedirs(ui_dest)
        copy_tree(ui_src, ui_dest)
        unlink(join(ui_dest, 'index.html'))
    return status


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('current version: %s' % __version__)
    ctx.exit()


@click.command()
@click.argument('destination', required=True)
@click.option('-s', '--swagger-doc',
              required=True, help='Swagger doc file.')
@click.option('-f', '--force',
              default=False, is_flag=True, help='Force overwrite.')
@click.option('-p', '--package',
              help='Package name / application name.')
@click.option('-t', '--template-dir',
              help='Path of your custom templates directory.')
@click.option('--spec', '--specification',
              default=False, is_flag=True,
              help='Generate online specification json response.')
@click.option('--ui',
              default=False, is_flag=True,
              help='Generate swagger ui.')
@click.option('--validate',
              default=False, is_flag=True,
              help='Validate swagger file.')
@click.option('-tlp', '--templates',
              default='flask',
              help='gen flask/tornado/falcon/sanic templates, default flask.')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show current version.')
def generate(destination, swagger_doc, force=False, package=None,
             template_dir=None, templates='flask',
             specification=False, ui=False, validate=False):
    package = package or destination.replace('-', '_')
    data = spec_load(swagger_doc)
    if validate:
        try:
            validate_spec(data)
            click.echo("Validation passed")
        except SwaggerValidationError as e:
            raise click.ClickException(str(e))
    #print 'data             ',data
    swagger = Swagger(data)
    if templates == 'tornado':
        generator = TornadoGenerator(swagger)
    elif templates == 'falcon':
        generator = FalconGenerator(swagger)
    elif templates == 'sanic':
        generator = SanicGenerator(swagger)
    else:
        generator = FlaskGenerator(swagger)
    generator.with_spec = specification
    generator.with_ui = ui
    template = Template()
    if template_dir:
        template.add_searchpath(template_dir)
    env = dict(package=package,
               module=swagger.module_name)

    if ui:
        ui_dest = join(destination, '%(package)s/static/swagger-ui' % env)
        ui_src = join(dirname(__file__), 'templates/ui')
        status = _copy_ui_dir(ui_dest, ui_src)
        click.secho('%-12s%s' % (status, ui_dest))

    for code in generator.generate():
        source = template.render_code(code)
        dest = join(destination, code.dest(env))
        dest_exists = exists(dest)
        can_override = force or code.override
        statuses = {
            (False, False): 'generate',
            (False, True): 'generate',
            (True, False): 'skip',
            (True, True): 'override'
        }
        status = statuses[(dest_exists, can_override)]
        click.secho('%-12s' % status, nl=False)
        click.secho(dest)

        if status != 'skip':
            write(dest, source)
