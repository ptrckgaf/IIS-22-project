from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
engine = create_engine('mysql+mysqldb://sql7581590:C3JvfZBW1z@sql7.freemysqlhosting.net:3306/sql7581590')
Base = declarative_base()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
from iis_wis2 import routes
