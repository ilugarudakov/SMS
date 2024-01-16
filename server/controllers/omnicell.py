from ..helpers import OmnisellTask
from ..requests import OmnisellRequest
from time import sleep


class Omnicell:

    @staticmethod
    def create_mailing() -> None:

        task = OmnisellTask()
        orequest = OmnisellRequest()
        # OmnisellTask().get_all_tasks_last_day()
        task.chek_ttl()
        # Moved to sheduler
        # OmnisellTask.update_individual_accepted_tasks()  # уточняем статусы принятых к отправке груп сообщений
        # OmnisellTask.update_single_accepted_tasks()
        messages = task.get_new_messages()  # выгребаем сообщения из msgcollector
        task.make_mailing(messages)  # формируем задания для лайфа
        individual_tasks = task.get_individual_tasks()
        if individual_tasks:
            resp = orequest.send(individual_tasks)  # пробуем отправить
            if resp and resp.status_code == 200:
                task.update_message_statuses(messages)  # помечаем ссобщения как обработанные
                sleep(5)
                task.update_tasks(resp, individual_tasks)  # обновляем статусы в тасках

        single_tasks = task.get_single_tasks()
        if single_tasks:
            resp = orequest.send(single_tasks)
            if resp and resp.status_code == 200:
                task.update_message_statuses(messages)  # помечаем ссобщения как обработанные
                sleep(5)
                task.update_tasks(resp, single_tasks)  # обновляем статусы в тасках
