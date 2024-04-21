from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, TimeField
from wtforms.validators import DataRequired


class SleepForm(FlaskForm):
    switch_on = TimeField("Включить в")
    submit = SubmitField('Установить')

