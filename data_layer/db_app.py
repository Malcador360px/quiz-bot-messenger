import config
from flask_sqlalchemy import SQLAlchemy

db_app = config.app
db_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE
db_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(db_app, session_options={'expire_on_commit': False})
