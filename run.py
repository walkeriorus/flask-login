from tienda import app
from database import db
from tienda.config import DefaultSettings
from flask_login import LoginManager
from tienda.user.models import User

from webbrowser import open_new_tab


app.env="development"
app.config.from_object( DefaultSettings )

db.init_app(app)

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(db,user_id)


open_new_tab("http://localhost:5000/")
app.run()