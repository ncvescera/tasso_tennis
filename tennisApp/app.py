from flask import Flask, render_template, url_for,  request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from models import User

app = Flask(__name__)   # inizializzo l'app
db = SQLAlchemy(app)    # inizializzo il gestore del DB
bcrypt = Bcrypt(app)    # inizializzo il coso per criptare le password

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


if __name__ == "__main__":
    import config
    from routes import *
    from api import *

    db.create_all()
    app.run(host="0.0.0.0", port="8080")

    
