from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL

db = SQLAlchemy()

class HomePosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(DECIMAL(precision=20, scale=15), nullable=False)
    longitude = db.Column(DECIMAL(precision=20, scale=15), nullable=False)
    altitude = db.Column(DECIMAL(precision=20, scale=15), nullable=False)