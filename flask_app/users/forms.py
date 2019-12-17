from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_app.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords did not match")])

    firstInterest = StringField("Interest 1", validators=[DataRequired()])
    secondInterest = StringField("Interest 2", validators=[DataRequired()])
    thirdInterest = StringField("Interest 3", validators=[DataRequired()])

    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already taken")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    token = StringField('Token', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Login")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError("That username does not exist in our database.")

    def validate_token(self, token):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None and not user.verify_totp(token.data):
            raise ValidationError("Invalid Token")

class UpdateInterestsForm(FlaskForm):
    firstInterest = StringField("Interest 1", validators=[DataRequired()])
    secondInterest = StringField("Interest 2", validators=[DataRequired()])
    thirdInterest = StringField("Interest 3", validators=[DataRequired()])
    submit = SubmitField("Update")
