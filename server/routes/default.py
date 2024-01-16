from ..app import app
from flask import render_template, url_for, flash, redirect, Markup, current_app, Response
from ..forms import LoginForm, SearchForm, SendSmsForm
from ..requests import OmnisellRequest
from ..rpc import check_text, clear_phone
from ..userlogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from ..helpers import UserHelper, OmnisellTask
from typing import Union
from logger import logger

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам.'
login_manager.login_message_category = 'alert-info'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


@app.route('/', methods=['GET', 'POST'])
@login_required
def default_route() -> Union[Response, str]:
    sms_form = SendSmsForm()
    search_form = SearchForm()
    result = object
    if sms_form.validate_on_submit():
        phone = clear_phone(sms_form.phone.data)
        text = check_text(sms_form.text.data)
        if text and phone:
            logger.info(f'{current_user.getName()} trying to send message.')
            response = OmnisellRequest().send_single(text, phone)
            logger.info(str(response.text))
            flash('Сообщение отправлено', category='alert-success')
            return redirect(url_for('default_route'))
        flash('Похоже, что номер неправильный', category='alert-danger')
        logger.warning(f'{current_user.getName()} entering incorrect data')
        return redirect(url_for('default_route'))

    if search_form.validate_on_submit():
        if len(search_form.data.data) > 9:
            param = clear_phone(search_form.data.data)
        else:
            param = search_form.data.data
        result = OmnisellTask().get_all_tasks(param)
        if result:
            flash(Markup(show_search_results(result)), category='alert-info')
            return redirect(url_for('default_route'))
        else:
            flash(f'По запросу {search_form.data.data} ничего не нашли', category='alert-warning')
            return redirect(url_for('default_route'))

    return render_template('index.html', title='Отправить СМС', sms_form=sms_form, search_form=search_form,
                           search_res=result, username=current_user.getName())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('default_route'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = UserHelper.get_user_by_name(login_form.login.data)
        if user and check_password_hash(user.password, login_form.psw.data):
            userlogin = UserLogin().create(user)
            rm = login_form.remember.data
            login_user(userlogin, remember=rm)
            logger.info(f' {current_user.getName()} is autenticated')
            return redirect(url_for('default_route'))
        else:
            flash('Неверная пара логин/пароль', category='alert-danger')
    return render_template('login.html', title='Авторизация', login_form=login_form)

@app.route('/logout')
@login_required
def logout():
    logger.info(f' {current_user.getName()} is logging out')
    logout_user()
    flash('Вы вышли из профиля', category='alert-success')
    return redirect(url_for('login'))


def show_search_results(res) -> str:
    if res:
        header = '<h4 class="alert-heading">Результаты поиска:</h4> <hr>'
        html_table = "<table class='table table-sm table-hover'> <thead class='thead-dark'>\n" \
                     "<tr>\n<th>Дата  время </th>\n<th>Договор</th>\n<th>Телефон</th>\n" \
                     "<th>Текст</th>\n<th>Статус</th>\n</tr>\n</thead>\n</tbody>"
        for i in res:
            html_table += f'<tr> <td><b>{str(i.delivery_date)}</b></td><td><b>{str(i.message.account)}</b></td>' \
                          f'<td><b>{str(i.message.phone)}</b></td><td><b>{str(i.message.text)}</b></td>' \
                          f'<td><b>{str(i.status.value)}</b></td></tr>'
        html_table += '</tbody></table>'
        return header + html_table
    return ''

@app.before_first_request
def before_first_request():
    DEPLOY_VERSION = ""
    try:
        with open("deploy_version.txt", "r") as dv_file:
            DEPLOY_VERSION = dv_file.readline().strip()
    except Exception as ex:
        pass
    current_app.DEPLOY_VERSION = DEPLOY_VERSION

@app.route('/healthcheck')
def health_check():
    return f"HealthCheck:version={current_app.DEPLOY_VERSION};status=ok"
