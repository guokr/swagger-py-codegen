import os

from jinja2 import Environment, FileSystemLoader


class Code(object):

    template = 'code.tpl'
    dest_template = '%(package)s/%(basePath)s'
    override = False

    def __init__(self, data=None, dist_template=None, dist_env=None):
        self.data = data or {}
        self.dest_template = dist_template or self.dest_template
        self.dist_env = dist_env or {}

    def dest(self, env=None):
        env = env or {}
        env.update(self.dist_env)
        return self.dest_template % env

    def before_render(self, jinja_env):
        pass


class CodeGenerator(object):

    dependencies = []

    def __init__(self, swagger):
        self.swagger = swagger

    def _dependence_callback(self, code):
        return code

    def _process(self):
        raise NotImplementedError

    def generate(self):
        for clz in self.dependencies:
            dependence = clz(self.swagger)
            g = dependence.generate()
            for code in g:
                yield self._dependence_callback(code)

        for code in self._process():
            yield code


class Template(object):

    def __init__(self):
        self.loader = FileSystemLoader(os.path.join(
            os.path.dirname(__file__), 'templates'))
        self.env = Environment(loader=self.loader)

    def add_searchpath(self, path):
        self.loader.searchpath.insert(0, path)

    def render(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def render_code(self, code):
        code.before_render(self)
        return self.render(code.template, **code.data)

