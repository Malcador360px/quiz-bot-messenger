import os
import sys
from flask import Flask

# Folders
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
RESOURCE_FOLDER = os.path.join(THIS_FOLDER, "resources")

THIS_SERVER_ID = "e76feab9-5964-4b14-9865-7a2518c2863b"
THIS_SERVER_AUTH_KEY = "VHhEaE7Uf755KhMqq8BghTdT"

# Flask application
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)

# Flask server port
SERVER_PORT = 5000

# Database url
DATABASE = "postgresql://quiz_marketing_bot:quiz_marketing_bot@localhost:5432/quiz_marketing_bot_db"

# Web interface url
WEB_INTERFACE = "http://localhost:8085"
