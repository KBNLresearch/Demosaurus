import os

from flask import Flask, render_template, request, redirect, send_from_directory
from flask_jsglue import JSGlue

def create_app(test_config=None, SECRET_KEY='dev', instance_path = ''):
    # create and configure the app
    if not instance_path:
        app = Flask(__name__, instance_relative_config=True)
    else:
        app = Flask(__name__, instance_path=instance_path)
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


    from . import db
    db.init_app(app)

    from . import publication
    app.register_blueprint(publication.bp)

    from . import link_thesaurus
    app.register_blueprint(link_thesaurus.bp)

    from . import subject_headings
    app.register_blueprint(subject_headings.bp)    

    from . import contributor
    app.register_blueprint(contributor.bp)



    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/')
    def index():
        return render_template('/')

    return app
