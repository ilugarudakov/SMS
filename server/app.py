from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__, template_folder=Config.TEMPLATES_DIR)
app.config.from_object(Config.FLASK_CONFIG)
db = SQLAlchemy(app)
