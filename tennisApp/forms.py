from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, TimeField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=40)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    landowner = BooleanField('Landowner?')
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=40)])
    submit = SubmitField('Login')


class AddFieldForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    description = TextAreaField()
    address = StringField('Address', validators=[DataRequired(), Length(min=2, max=60)])
    available_from = TimeField('Apertura', validators=[DataRequired()])
    available_to =  TimeField('Chiusura', validators=[DataRequired()])
    price_h = FloatField('Prezzo orario', validators=[DataRequired()])
    submit = SubmitField('Add Field')

    def as_dict(self):
        res = {
            'name': str(self.name.data),
            'description': str(self.description.data),
            'address': str(self.address.data),
            'available_from': str(self.available_from.data),
            'available_to': str(self.available_to.data),
            'price_h': str(self.price_h.data)
        }

        return res