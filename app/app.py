from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking (optional)

db = SQLAlchemy(app)

if __name__ == '__main__':
    from wa_webhook import *

    app.run(host='0.0.0.0', port=5000, debug=True)