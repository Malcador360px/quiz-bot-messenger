from sqlalchemy import text
from telegram import ReplyKeyboardRemove
from data_layer.db_app import db
from dateutil.parser import parse
from telegram.ext import *
from utils.quiz_utils import *
from utils.db_utils import *
from enums.input_structure import *
from models.bot_models import TelegramBot, QuizBot
from models.manager_models import BotManagerInterface


class QuizTelegramBot(TelegramBot, QuizBot):

    def __init__(self, manager: BotManagerInterface, quiz_json_data: dict,
                 table_name: str, schema_name: str, bot_id=None):
        TelegramBot.__init__(self, manager, bot_id=bot_id)
        QuizBot.__init__(self, quiz_json_data, table_name, schema_name)
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message))

    def start(self, update, context):
        sender_id = update.message.from_user.id
        with db.get_engine().connect() as con:
            if not self.multiple_registration and get_objects_by_messenger_id(con, self.table, self.schema, sender_id):
                self.telegram_bot.send_message(update.message.chat.id, "Your are already registered, thank you!",
                                               reply_markup=ReplyKeyboardRemove())
            else:
                first_question = list(self.quiz.keys())[0]
                answers = self.quiz[first_question].get(JSONKeys.answers.value)
                if answers is None:
                    self.telegram_bot.send_message(update.message.chat.id, first_question,
                                                   reply_markup=ReplyKeyboardRemove())
                else:
                    self.telegram_bot.send_message(update.message.chat.id, first_question,
                                                   reply_markup=create_keyboard(answers))
                self.users_answers[sender_id] = {}

    def handle_message(self, update, context):
        sender_id = update.message.from_user.id
        chat_id = update.message.chat.id
        message = update.message.text
        questions = list(self.quiz.keys())

        if sender_id in self.users_answers:
            for index, question in enumerate(questions):
                if question in self.users_answers[sender_id]:
                    pass
                else:
                    answers = self.quiz[question].get(JSONKeys.answers.value)
                    custom_answer = self.quiz[question].get(JSONKeys.custom_answer.value)
                    if answers is None:
                        answers = []
                    if custom_answer:
                        if self.__check_custom_answer_format(message, chat_id, formats=custom_answer):
                            self.users_answers[sender_id][question] = message
                            if (index + 1) < len(questions):
                                next_question = questions[index + 1]
                                next_answers = self.quiz[next_question].get(JSONKeys.answers.value)
                                if next_answers is None:
                                    self.telegram_bot.send_message(chat_id, next_question,
                                                                   reply_markup=ReplyKeyboardRemove())
                                else:
                                    self.telegram_bot.send_message(chat_id, next_question,
                                                                   reply_markup=create_keyboard(next_answers))
                            else:
                                self.__save_in_db(sender_id)
                                del self.users_answers[sender_id]
                                self.telegram_bot.send_message(chat_id, "Thank you for your answers!",
                                                               reply_markup=ReplyKeyboardRemove())
                        break
                    elif message in answers:
                        self.users_answers[sender_id][question] = message
                        if (index + 1) < len(questions):
                            next_question = questions[index + 1]
                            next_answers = self.quiz[next_question].get(JSONKeys.answers.value)
                            if next_answers is None:
                                self.telegram_bot.send_message(chat_id, next_question,
                                                               reply_markup=ReplyKeyboardRemove())
                            else:
                                self.telegram_bot.send_message(chat_id, next_question,
                                                               reply_markup=create_keyboard(next_answers))
                        else:
                            self.__save_in_db(sender_id)
                            del self.users_answers[sender_id]
                            self.telegram_bot.send_message(chat_id, "Thank you for your answers!",
                                                           reply_markup=ReplyKeyboardRemove())
                        break
                    else:
                        self.telegram_bot.send_message(chat_id, "Invalid answer")
                        break
        else:
            self.start(update, context)

    def __check_custom_answer_format(self, message, chat_id, formats=None):
        if formats is None:
            formats = [Formats.any.value]

        incorrect_format_message = "Your answer has wrong format, please enter "
        for format in formats:
            incorrect_format_message += format + " or "
            if format == Formats.any.value:
                return True
            elif format == Formats.only_letters.value and message.isalpha():
                return True
            elif format == Formats.integer.value and message.isnumeric():
                return True
            elif format == Formats.date.value and self.__is_date(message):
                return True
            elif format == Formats.person_name.value and check_person_name(message):
                return True
            elif format == Formats.phone_number.value and check_phone_number(message):
                return True
            elif format == Formats.email_address.value and check_email_address(message):
                return True
        incorrect_format_message = incorrect_format_message[:-4]
        self.telegram_bot.send_message(chat_id, incorrect_format_message)
        return False

    def __save_in_db(self, sender_id):
        data = {StandardColumns.id.value: uuid.uuid4(),
                StandardColumns.messenger_id.value: sender_id,
                StandardColumns.created.value: datetime.datetime.utcnow(),
                StandardColumns.updated.value: datetime.datetime.utcnow()}
        columns = f'{StandardColumns.id.value}, {StandardColumns.messenger_id.value},' \
                  f' {StandardColumns.created.value}, {StandardColumns.updated.value}, '
        values = f':{StandardColumns.id.value}, :{StandardColumns.messenger_id.value},' \
                 f' :{StandardColumns.created.value}, :{StandardColumns.updated.value}, '
        i = 1
        for question in self.users_answers[sender_id].keys():
            if JSONKeys.table_column.value in self.quiz[question]:
                data[f'param{i}'] = self.users_answers[sender_id][question]
                columns += f'"{self.quiz[question][JSONKeys.table_column.value]}", '
                values += f':param{i}, '
                i += 1
        columns = columns[:-2]
        values = values[:-2]
        statement = text(f'INSERT INTO "{self.schema}"."{self.table}"({columns}) VALUES({values})')
        with db.get_engine().connect() as con:
            con.execute(statement, **data)
            db.session.commit()

    @staticmethod
    def __is_date(string, fuzzy=False):
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False
