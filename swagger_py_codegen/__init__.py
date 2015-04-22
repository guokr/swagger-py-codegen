# -*- coding: utf-8 -*-
import codecs
import click

from parser import parse_yaml
import writer

__version__ = '0.0.6'


@click.command()
@click.argument('path', required=True)
@click.option('-s', '--swagger-doc', required=True, help='Swagger doc file.')
@click.option('-f', '--force', is_flag=True, help='Force overwrite.')
@click.option('-a', '--appname', help='Application name or package name.')
def codegen(path, swagger_doc, force=False, appname=None):
    if appname is None:
        appname = path.split('/')[-1].replace('-', '_')

    with codecs.open(swagger_doc, 'r', 'utf-8') as f:
        m = parse_yaml(f)
    if not m:
        print 'swagger-doc could not be read.'
        exit(-1)

    writer.write(m, path, appname, force)

if __name__ == '__main__':
    codegen()
