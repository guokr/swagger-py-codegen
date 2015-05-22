# -*- coding: utf-8 -*-
import codecs
import click

from parser import parse_yaml
import writer

__version__ = '0.0.9'


@click.command()
@click.argument('path', required=True)
@click.option('-s', '--swagger-doc', required=True, help='Swagger doc file.')
@click.option('-f', '--force', is_flag=True, help='Force overwrite.')
@click.option('-a', '--appname', help='Application name or package name.')
@click.option('--specification', is_flag=True, help='Generate online specification.')
@click.option('--ui', is_flag=True, help='Generate swagger ui.')
def codegen(path, swagger_doc, force=False, appname=None, specification=True, ui=True):
    if appname is None:
        appname = path.split('/')[-1].replace('-', '_')

    with codecs.open(swagger_doc, 'r', 'utf-8') as f:
        m = parse_yaml(f)
    if not m:
        print 'swagger-doc could not be read.'
        exit(-1)

    if specification:
        import yaml
        import model
        res = model.Resource('/_swagger', m)
        method = model.Method('get', res)
        with codecs.open(swagger_doc, 'r', 'utf-8') as f:
            method.response_example = yaml.load(f)
        res.methods = {'GET': method}
        m.add_resource(res)

    writer.write(model=m, base_path=path, appname=appname,
                 overwrite=force, ui=ui)

if __name__ == '__main__':
    codegen()
