from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField


class NewsForm(FlaskForm):
    file = FileField('')
    content = TextAreaField("Исполнитель")
    submit = SubmitField('Добавить')

