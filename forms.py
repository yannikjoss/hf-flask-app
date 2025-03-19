# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime

class CommentForm(FlaskForm):
    body = TextAreaField('Ihr Kommentar', validators=[DataRequired(), Length(min=1, max=280)]) #Limit für Kommentare
    submit = SubmitField('Kommentieren')

class AppointmentForm(FlaskForm):
    name = StringField('Veranstaltungsname', validators=[DataRequired(), Length(max=120)])
    date = DateTimeField('Datum', validators=[DataRequired()], format='%Y-%m-%dT%H:%M') #Enables datetime-local input
    location = StringField('Ort', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Beschreibung')
    submit = SubmitField('Termin erstellen')