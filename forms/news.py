from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Исполнитель', validators=[DataRequired()])
    content = TextAreaField("Название")
    is_private = BooleanField("Личное")
    submit = SubmitField('Добавить')
