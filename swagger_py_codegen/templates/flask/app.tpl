# -*- coding: utf-8 -*-
from flask import Flask

import {{ blueprint }}


def create_app():
    app = Flask(__name__, static_folder='static')
    app.register_blueprint(
        {{ blueprint }}.bp,
        url_prefix='{{ base_path }}')
    return app

if __name__ == '__main__':
    create_app().run(debug=True)
