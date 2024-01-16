from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField, TelField
from wtforms.validators import Email, Length, DataRequired, EqualTo, NumberRange


class LoginForm(FlaskForm):
    login = StringField('Логин: ', validators=[DataRequired(), Length(min=3, max=20)])
    psw = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=3, max=20)])
    remember = BooleanField('Запомнить меня: ', default=True)
    submit = SubmitField('Войти')


class SendSmsForm(FlaskForm):
    phone = TelField('Телефон: ', validators=[DataRequired(), Length(min=10, max=13)],
                     render_kw={"placeholder": "Пример: 0961234567"})

    text = TextAreaField('Текст сообщения:', validators=[DataRequired(), Length(min=2, max=200)],
                         render_kw={"placeholder": "Не более 200 знаков"})
    submit = SubmitField('Отправить смс')


class SearchForm(FlaskForm):
    data = StringField('', validators=[DataRequired(), Length(min=1, max=13)],
                       render_kw={"placeholder": "Договор или телефон:"}
                       )
    submit = SubmitField('Найти')
