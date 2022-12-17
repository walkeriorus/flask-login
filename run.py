from tienda import app
from database import db
from tienda.config import DefaultSettings
from user import User
from flask_login import LoginManager


app.env="development"
app.config.from_object( DefaultSettings )

db.init_app(app)

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get(db,user_id)



app.run()