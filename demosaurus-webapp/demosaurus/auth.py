from flask_login import LoginManager
from demosaurus.models import UserModel

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
