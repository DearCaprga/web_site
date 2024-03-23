from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField


class NewsForm(FlaskForm):
    file = FileField('')
    content = TextAreaField("Исполнитель")
    is_private = BooleanField("Личное")
    submit = SubmitField('Добавить')

