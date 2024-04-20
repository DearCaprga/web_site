from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField


class NewsForm(FlaskForm):
    file = FileField('Загрузите песню')
    content = StringField("Исполнитель")
    submit = SubmitField('Добавить')

