from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = "\x8a\xbe\xa6\x86\x01D\x03\xfdt\xb8*\x9f\xae\x86\xad\xaf"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Tphuy150200mysql@@localhost/airlineht?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['ROOT_PROJECT_PATH'] = app.root_path

db = SQLAlchemy(app)

admin = Admin(app=app, name="Vietnam Airlines Management", template_mode="bootstrap4")

login = LoginManager(app=app)
