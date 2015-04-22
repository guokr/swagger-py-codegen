# -*- coding: utf-8 -*-
from os import makedirs
from os.path import join as pj, exists, isdir
import codecs

from .generator import Generator


def echo(string, level='info'):
    color = dict(
        info='\033[92m',
        warn='\033[93m'
    )
    end = '\033[0m'
    print '%s%s%s' % (color[level], string, end)


def write(model, base_path, app_name='app', overwrite=False):
    app_path = pj(base_path, app_name)
    bp_path = pj(app_path, model.blueprint)
    api_path = pj(bp_path, 'api')
    if not isdir(api_path):
        makedirs(api_path)

    layouts = dict(
        requirements=dict(
            path=pj(base_path, 'requirements.txt'),
            overwrite=False),
        app=dict(
            path=pj(app_path, '__init__.py'),
            overwrite=False),
        blueprint=dict(
            path=pj(bp_path, '__init__.py'),
            overwrite=False),
        api=dict(
            path=pj(api_path, '__init__.py'),
            overwrite=False),
        routes=dict(
            path=pj(bp_path, 'routes.py'),
            overwrite=True),
        schemas=dict(
            path=pj(bp_path, 'schemas.py'),
            overwrite=True),
        validators=dict(
            path=pj(bp_path, 'validators.py'),
            overwrite=True),
        filters=dict(
            path=pj(bp_path, 'filters.py'),
            overwrite=True),
    )

    g = Generator(model)

    for item, info in layouts.iteritems():
        if info['overwrite'] or overwrite or not exists(info['path']):
            _write(getattr(g, 'generate_%s' % item)(), info['path'])
            echo('"' + info['path'] + '" generated.', 'warn')
        else:
            echo('"' + info['path'] + '" already exists, skipped.')

    for name, view in g.generate_views():
        path = pj(api_path, '%s.py' % name)
        if overwrite or not exists(path):
            _write(view, path)
            echo('"' + path + '" generated.', 'warn')
        else:
            echo('"' + path + '" already exists, skipped.')


def _write(content, filename):
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(content)
