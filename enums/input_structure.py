from enum import Enum


class JSONKeys(Enum):
    client_data = "client_data"
    shutdown = "shutdown"
    server_id = "server_id"
    auth_key = "auth_key"
    server_url = "server_url"
    user_identifier = "user_identifier"
    request_keyword = "request_keyword"
    table_json = "table_json"
    quiz_json = "quiz_json"
    multiple_registration = "multiple_registration"
    answers = "answers"
    custom_answer = "custom_answer"
    table_column = "table_column"
    table_name = "table_name"
    fetch_what = "fetch_what"
    tables = "tables"
    bots = "bots"
    all_entries = "all_entries"
    new_entries = "new_entries"
    api_token = "api_token"


class RequestKeywords(Enum):
    create = "create"
    update = "update"
    fetch = "fetch"
    check = "check"
    stop = "stop"
    delete = "delete"


class FetchKeywords(Enum):
    info = "info"
    quiz = "quiz"
    csv = "csv"
    excel = "excel"


class Formats(Enum):
    any = "any"
    only_letters = "only_letters"
    integer = "integer"
    date = "date"
    person_name = "person_name"
    phone_number = "phone_number"
    email_address = "email_address"
