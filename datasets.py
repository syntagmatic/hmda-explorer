from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/db/datasets.db'
db = SQLAlchemy(app)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=False)
    filename = db.Column(db.String(300), unique=True)
    last_modified = db.Column(db.DateTime)

    def __init__(self, filename):
        self.name = filename
        self.filename = filename
        self.last_modified = datetime.utcnow()

    def __repr__(self):
        return '<Dataset %r>' % self.name
