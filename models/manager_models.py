from enums.columns import BotColumns
from data_layer.orm_classes import Bot
from data_layer.db_app import db


class BotManagerInterface:

    def deploy_bot(self, bot_id=None) -> Bot:
        pass

    def discharge_bot(self, bot: Bot) -> None:
        pass


class StaticBotManager(BotManagerInterface):

    db = db

    def __init__(self):
        pass

    @classmethod
    def add_new_bot(cls, api_token: str, bot_id=None, active=None):
        record = {BotColumns.api_token.value: api_token}
        if bot_id:
            record[BotColumns.id.value] = bot_id
        if active:
            record[BotColumns.active.value] = active
        Bot.add_bot(db.session, record)

    @classmethod
    def deploy_bot(cls, bot_id=None):
        if bot_id:
            bot = Bot.get_bot_by_id(db.session, bot_id)
        else:
            bot = cls.__get_idle_bot()

        if bot is None:
            raise RuntimeError("No bots now available")
        Bot.set_active(db.session, bot.id, True)
        return bot

    @classmethod
    def discharge_bot(cls, bot):
        Bot.set_active(db.session, bot.id, False)

    @classmethod
    def __get_idle_bot(cls):
        return Bot.get_idle_bot(db.session)


class DynamicBotManager(BotManagerInterface):

    def __init__(self):
        pass
