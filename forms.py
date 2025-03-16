# forms.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    body = TextAreaField('Ihr Kommentar', validators=[DataRequired(), Length(min=1, max=280)]) #Limit für Kommentare
    submit = SubmitField('Kommentieren')