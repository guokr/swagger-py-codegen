# -*- coding: utf-8 -*-
from flask import Flask

import {{ model.blueprint }}


def create_app():
    app = Flask(__name__)
    app.register_blueprint(
        {{ model.blueprint }}.bp,
        url_prefix='/{{ model.blueprint }}')
    return app

if __name__ == '__main__':
    create_app().run(debug=True)
