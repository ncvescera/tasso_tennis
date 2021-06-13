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
    landowner_id = db.Column(db.String(30), db.ForeignKey('user.id'), default=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': str(self.name),
            'description': str(self.description),
            'address': str(self.address),
            'available_from': str(self.available_from)[:-3],
            'available_to': str(self.available_to)[:-3],
            'price_h': str(self.price_h),
            'landowner_id': self.landowner_id
        }

class Prenotation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id', ondelete='CASCADE'))
    player_id = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)
    price = db.Column(db.Float, nullable=False)
    __table_args__ = (db.UniqueConstraint('field_id', 'date', 'start', 'end', name='_prenotation_uc'),)

    def as_dict(self):
        return {
            'id': str(self.id),
            'field_id': self.field_id,
            'player_id': str(self.player_id),
            'date': str(self.date),
            'start': str(self.start)[:-3],
            'end': str(self.end)[:-3],
            'price': str(round(self.price, 1))
        }