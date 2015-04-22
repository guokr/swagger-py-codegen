# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, FileSystemLoader


class Generator(object):

    def __init__(self, model):
        super(Generator, self).__init__()
        self.model = model
        loader = FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates'))
        self.env = Environment(loader=loader)

    def render(self, template, *args, **kwargs):
        template = self.env.get_template(template)
        return template.render(*args, **kwargs)

    def generate_requirements(self):
        return self.render('requirements.tpl')

    def generate_routes(self):
        return self.render(
            'routes.tpl',
            routes=self.model.routes, resources=self.model.resources)

    def generate_schemas(self):
        return self.render('schemas.tpl', schemas=self.model.schemas)

    def generate_validators(self):
        return self.render('validators.tpl', validators=self.model.validators)

    def generate_filters(self):
        return self.render('filters.tpl', filters=self.model.filters)

    def generate_views(self):
        for view, ins in self.model.resources_group.iteritems():
            yield (view, self.render('views.tpl', resources=ins))

    def generate_init(self):
        return self.render('init.tpl')

    def generate_api(self):
        return self.render('api.tpl')

    def generate_app(self):
        return self.render('app.tpl', model=self.model)

    def generate_blueprint(self):
        return self.render('blueprint.tpl', model=self.model)

    def generate_view_tests(self):
        for view, ins in self.model.resources_group.iteritems():
            yield (view, self.render('view_test.tpl', resources=ins))
