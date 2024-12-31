from telegram.ext import *
from models.bot_models import TelegramBot, ControlBot


class ControlTelegramBot(TelegramBot, ControlBot):

    def __init__(self, http_telegram_token):
        TelegramBot.__init__(self, http_telegram_token)
        ControlBot.__init__(self)
        self.dispatcher.add_handler(CommandHandler("start", self.start))

    def start(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def register(self):
        pass

    def get_all(self):
        pass

    def get_all_new(self):
        pass

    def get_all_from_date(self):
        pass
