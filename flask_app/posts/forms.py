from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

class CreatePostForm(FlaskForm):
    title = StringField("Add a title!", validators=[DataRequired(), Length(min=5, max=100)])
    link = StringField("Link", validators=[DataRequired(), Regexp(regex="^.*\.gif$", message="Make sure that the link has a .gif extension!")]) 
    submit = SubmitField("Submit GIF Post!")