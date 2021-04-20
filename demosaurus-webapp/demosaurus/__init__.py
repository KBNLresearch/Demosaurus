import os

from flask import Flask, render_template, request, redirect
from flask_jsglue import JSGlue
from flask_login import login_required, current_user, login_user, logout_user
from demosaurus.models import UserModel, db_users
from demosaurus.auth import login_manager


def create_app(test_config=None, SECRET_KEY='dev'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'demosaurus.sqlite'),
    )
    jsglue = JSGlue()
    jsglue.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db_users.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'


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

    from . import contributor
    app.register_blueprint(contributor.bp)



    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # User login stuff.
    @app.before_first_request
    def create_all():
        db_users.create_all()

    @app.route('/')
    @login_required
    def index():
        return render_template('/')

    # Method for login view.
    @app.route('/login', methods = ['POST', 'GET'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')

        if request.method == 'POST':
            email = request.form['email']
            user = UserModel.query.filter_by(email=email).first()
            if user is not None and user.check_password(request.form['password']):
                login_user(user)
                return redirect('/')

        return render_template('login.html')

    # Register new user method.
    @app.route('/register', methods=['POST', 'GET'])
    def register():
        if current_user.is_authenticated:
            return redirect('/')

        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            if UserModel.query.filter_by(email=email).first():
                return ('Email already Present')

            user = UserModel(email=email, username=username)
            user.set_password(password)
            db_users.session.add(user)
            db_users.session.commit()
            return redirect('/login')
        return render_template('register.html')

    # Logout method.
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')


    return app
