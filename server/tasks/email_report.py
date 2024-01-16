from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from server.helpers.omnisell import OmnisellTask
from logger import logger


class EmailReport:
    def __init__(self):
        self._server = SMTP(Config.EMAIL_PARAMS.SMTP_SERVER, Config.EMAIL_PARAMS.SMTP_PORT)

    @property
    def _make_text_body(self) -> MIMEText:
        text = 'Отчет по СМС за сутки.'
        return MIMEText(text, "plain")

    @property
    def _make_html_body(self) -> MIMEText:
        tasks = OmnisellTask().get_all_tasks_last_day()
        html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                table {
                  font-family: arial, sans-serif;
                  border-collapse: collapse;
                }
                td, th {
                  border: 1px solid #000000;
                  text-align: left;
                  padding: 4px;
                }
                tr:nth-child(even) {
                  background-color: #dddddd;
                }
                </style>
            </head>
            <body>'''
        html += '<h3> Отчет по статусам СМС за минувшие сутки</h3>\n'
        html += '<table>\n<tr>\n<th>Статус</th>\n<th>Количество</th>\n</tr>\n'

        report = {}
        for task in tasks:
            count = report.get(task.status.value, 0) + 1
            report.update({task.status.value: count})

        if not report:
            report.update({'Отсутствуют данные': ' ¯\_(ツ)_/¯ '})
        for elem in report:
            html += '<tr>\n'
            html += f'<td>{elem}</td>\n'
            html += f'<td>{report[elem]}</td>\n'
            html += '</tr>\n'

        html += '</table></body>'
        return MIMEText(html, "html")

    def send_email(self, recievers: str):
        message = MIMEMultipart("alternative")
        message["To"] = recievers
        message["Subject"] = Config.EMAIL_PARAMS.MESSAGE_SUBJECT
        message.attach(self._make_text_body)
        message.attach(self._make_html_body)
        try:
            self._server.sendmail(Config.EMAIL_PARAMS.SENDER_EMAIL, recievers, message.as_string())
        except Exception as err:
            logger.error(f'Can non send_email {err}')
