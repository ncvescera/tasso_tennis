from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    landowner = db.Column(db.Boolean(), default=False)

    def as_dict(self):
        return {
            'username': str(self.username),
            'name': str(self.name),
            'surname': str(self.surname),
            'email': str(self.email),
            'landowner': self.landowner
        }

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text)
    address = db.Column(db.String(60), nullable=False)
    available_from = db.Column(db.Time, nullable=False)
    available_to = db.Column(db.Time, nullable=False)
    price_h = db.Column(db.Float, nullable=False)
    landowner_id = db.Column(db.String(30), db.ForeignKey('user.username'), default=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': str(self.name),
            'description': str(self.description),
            'address': str(self.address),
            'available_from': str(self.available_from),
            'available_to': str(self.available_to),
            'price_h': str(self.price_h),
            'landowner_id': self.landowner_id
        }

class Prenotation(db.Model):
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), primary_key=True)
    player_id = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    date = db.Column(db.Date, primary_key=True, nullable=False)
    start = db.Column(db.Time, primary_key=True, nullable=False)
    end = db.Column(db.Time, nullable=False)
    price = db.Column(db.Float, nullable=False)
    

    def as_dict(self):
        return {
            'field_id': self.field_id,
            'player_id': str(self.player_id),
            'date': self.date,
            'start': self.start,
            'end': self.end,
            'price': self.price
        }