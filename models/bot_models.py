import json
from collections import OrderedDict
from models.manager_models import BotManagerInterface
import telegram
from telegram.ext import *
from enums.input_structure import *


class ControlBot:

    def __init__(self):
        pass

    def add_bot_to_control(self):
        pass


class QuizBot:

    def __init__(self, json_data: dict, table_name: str, schema_name: str):
        self.multiple_registration = False
        self.quiz = self.process_quiz(json_data)
        self.table = table_name
        self.schema = schema_name
        self.users_answers = {}

    def process_quiz(self, json_data):
        quiz = OrderedDict()
        multiple_registration = json_data.pop(JSONKeys.multiple_registration.value, None)
        if multiple_registration:
            self.multiple_registration = multiple_registration
        if not self.__check_quiz(json_data):
            return quiz
        else:
            for i in range(1, len(json_data) + 1):
                question = json_data[str(i)]
                key = list(question.keys())[0]
                quiz[key] = question[key]
        return quiz

    @staticmethod
    def __check_quiz(json_data):
        for key in json_data.keys():
            try:
                int(key)
                for item in json_data[key].items():
                    _, item = item
                    table_column = item.get(JSONKeys.table_column.value)
                    answers = item.get(JSONKeys.answers.value)
                    custom_answer = item.get(JSONKeys.custom_answer.value)

                    if table_column:
                        if not isinstance(table_column, str):
                            return False

                    if answers:
                        if not isinstance(answers, list):
                            return False

                        for answer in item[JSONKeys.answers.value]:
                            if not isinstance(answer, str):
                                return False

                    if custom_answer:
                        if not isinstance(custom_answer, list):
                            return False

                        for format in item[JSONKeys.custom_answer.value]:
                            if not isinstance(format, str):
                                return False
            except ValueError:
                print("Missing numeration")
                return False
            except KeyError:
                print("Incorrect JSON data format")
                return False
        return True


class TelegramBot:

    def __init__(self, manager: BotManagerInterface, bot_id=None):
        self.manager = manager
        self.bot = manager.deploy_bot(bot_id=bot_id)
        self.token = self.bot.api_token
        self.updater = Updater(self.token, use_context=True)
        self.telegram_bot = self.updater.bot
        self.telegram_bot.get_me()
        self.dispatcher = self.updater.dispatcher

    def get_telegram_username(self):
        return self.telegram_bot.username

    def start_webhook(self, base_url: str, drop_pending_updates=False, port=0, listen="0.0.0.0"):
        self.updater.start_webhook(webhook_url=f'{base_url}/{self.bot.id}', drop_pending_updates=drop_pending_updates,
                                   listen=listen, port=port, cert='quiz-bot.messenger.pem')

    def discharge_bot(self):
        self.stop_webhook()
        self.manager.discharge_bot(self.bot)

    def stop_webhook(self):
        self.updater.stop()

    def process_request(self, json_string):
        update = telegram.Update.de_json(json.loads(json_string), self.telegram_bot)
        self.dispatcher.process_update(update)
