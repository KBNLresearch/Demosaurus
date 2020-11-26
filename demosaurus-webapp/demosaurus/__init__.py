import os

from flask import Flask
from flask_jsglue import JSGlue


def create_app(test_config=None, SECRET_KEY = 'dev'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'demosaurus.sqlite'),
    )
    jsglue = JSGlue()
    jsglue.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import publication
    app.register_blueprint(publication.bp)
    app.add_url_rule('/', endpoint='overview')

    from . import link_thesaurus
    app.register_blueprint(link_thesaurus.bp)

    from . import contributor
    app.register_blueprint(contributor.bp)

    return app




