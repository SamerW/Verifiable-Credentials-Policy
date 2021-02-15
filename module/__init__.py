import os
from flask import Flask, request
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    babel = Babel(app)
    app.config.from_object('config.Config')
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @babel.localeselector
    def get_locale():
        available_languages = ["en", "fr"]
        return request.accept_languages.best_match(available_languages)

    db.init_app(app)
    with app.app_context():
        from . import profile_api, statement_api, policy_api, schema_api
        db.create_all()

    from . import core
    app.register_blueprint(core.bp)
    app.add_url_rule('/', endpoint='/credential_profile/create')

    return app
