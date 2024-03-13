from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    file = FileField('')
    # title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Исполнитель")
    is_private = BooleanField("Личное")
    submit = SubmitField('Добавить')

