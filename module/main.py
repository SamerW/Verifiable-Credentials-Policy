import os, sys
from flask import Flask, request
from flask_cors import CORS
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
import pathlib

db = SQLAlchemy()

if __name__ == '__main__':
    base_dir = pathlib.Path(__file__).parent.absolute()
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.join(sys._MEIPASS)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    app = Flask(__name__,
                static_folder=os.path.join(base_dir, 'static'),
                template_folder=os.path.join(base_dir, 'templates'))
    db_uri = os.path.join(application_path, 'cnl.sqlite')
    babel_uri = os.path.join(base_dir, 'translations')
    app.config.from_mapping(
        # General Config
        SECRET_KEY='dev',
        FLASK_APP='module',
        FLASK_ENV='development',
        # CORS
        CORS_HEADERS='Content-Type',
        # Database
        SQLALCHEMY_DATABASE_URI='sqlite:////'+db_uri,
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # Babel
        BABEL_TRANSLATION_DIRECTORIES=babel_uri
    )
    cors = CORS(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    babel = Babel(app)
    @babel.localeselector
    def get_locale():
        available_languages = ["en"]
        other_languages = os.listdir(os.path.join(base_dir, 'translations/'))
        for language in other_languages:
            available_languages.append(language)
        return request.accept_languages.best_match(available_languages)


    db.init_app(app)
    with app.app_context():
        import module.profile_api, module.statement_api, module.policy_api, module.schema_api, module.models
        db.create_all()
        self_issuer = module.models.Issuer.query.filter(
            module.models.Issuer.name == "self"
        ).first()
        all_prop = module.models.Property.query.filter(
            module.models.Property.name == "all"
        ).first()
        if not self_issuer:
            new_issuer = module.models.Issuer(
                name="self"
            )
            db.session.add(new_issuer)
            db.session.commit()
        if not all_prop:
            new_all_prop = module.models.Property(
                name="all"
            )
            db.session.add(new_all_prop)
            db.session.commit()


    import module.core

    app.register_blueprint(module.core.bp)
    app.add_url_rule('/', endpoint='/credential_profile/create')

    app.run(debug=False, host='0.0.0.0', port=5000)
