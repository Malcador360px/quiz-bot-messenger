from enum import Enum


class StandardColumns(Enum):
    id = "id"
    messenger_id = "messenger_id"
    created = "created"
    updated = "updated"


class BotColumns(Enum):
    id = "id"
    api_token = "api_token"
    active = "active"
    created = "created"
    updated = "updated"


class QuizColumns(Enum):
    id = "id"
    user_id = "user_id"
    table_name = "table_name"
    table = "table"
    quiz = "quiz"
    last_download = "last_download"
    created = "created"
    updated = "updated"


class BotQuizColumns(Enum):
    bot_id = "bot_id"
    bot_username = "bot_username"
    user_id = "user_id"
    table_name = "table_name"
    quiz = "quiz"
    created = "created"
    updated = "updated"


class ColumnTypes(Enum):
    auto = "Auto"
    text = "Text"
    integer = "Integer"
    datetime = "DateTime"
    json = "JSONB"
