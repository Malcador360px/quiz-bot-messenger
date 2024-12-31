from models.manager_models import *
from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError


class StaticTelegramBotManager(StaticBotManager):

    def __init__(self):
        StaticBotManager.__init__(self)


class DynamicTelegramBotManager(DynamicBotManager):

    session_name = 'Quiz Network'
    connection_timeout = 10

    bot_father = 'botfather'
    cancel_command = '/cancel'
    add_bot_command = '/newbot'
    delete_bot_command = '/deletebot'

    name_key = 'bot_name'
    username_key = 'bot_username'

    def __init__(self, api_id, api_hash, phone):
        DynamicBotManager.__init__(self)
        self.client = TelegramClient(self.session_name, api_id, api_hash)
        self.client.add_event_handler(self.message_handler, events.NewMessage(incoming=True))
        self.next_bot = {self.name_key: None, self.username_key: None}
        self.client.start(phone)
        self.login(phone)

    def login(self, phone):
        if not self.client.is_user_authorized():
            try:
                self.client.sign_in(phone, input("Code: "))
            except SessionPasswordNeededError:
                self.client.sign_in(phone, input("Password: "))

    def add_new_bot(self, bot_name, bot_username):
        print("START")
        self.next_bot[self.name_key] = bot_name
        self.next_bot[self.username_key] = bot_username
        self.client.connect()
        print("CONNECT")
        self.client.send_message(self.bot_father, self.cancel_command)
        print("CANCEL")
        self.client.send_message(self.bot_father, self.add_bot_command)
        print("SENT")

    def delete_bot(self):
        self.client.connect()
        self.client.send_message(self.bot_father, self.cancel_command)
        self.client.send_message(self.bot_father, self.delete_bot_command)

    async def message_handler(self, event):
        print("OK")
        if "choose a name" in event.raw_text:
            await event.reply(self.next_bot[self.name_key])
        elif "choose a username" in event.raw_text:
            await event.reply(self.next_bot[self.username_key])
        elif "HTTP API" in event.raw_text:
            result = event.raw_text[event.raw_text.find("HTTP API"):].split("\n")[1]
            print(result)
            await self.client.disconnect()
