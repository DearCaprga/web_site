from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, TimeField
from wtforms.validators import DataRequired


class SleepForm(FlaskForm):
    # title = StringField('Название', validators=[DataRequired()])
    switch_on = TimeField("Включить в")
    submit = SubmitField('Установить')

