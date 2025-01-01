import datetime
import os
import sys
import config
import json
import requests
import uuid
from enums.input_structure import *
from utils.db_utils import *
from utils.file_utils import *
from urllib3.exceptions import MaxRetryError, NewConnectionError
from telegram_aplication.quiz import QuizTelegramBot
from telegram_aplication.manager import StaticTelegramBotManager
from utils.server_utils import *
from data_layer.db_app import db
from data_layer.orm_classes import *
from flask import request, Response, send_file

app = config.app
external_url = f"https://3.126.63.200:{config.SERVER_PORT}"  # expose_port_ngrok(config.SERVER_PORT)
telegram_webhook_base = f'{external_url}/telegram'
whatsapp_webhook_base = f'{external_url}/whatsapp'
manager = StaticTelegramBotManager()
active_quiz_bots = dict()


def init():
    data = {JSONKeys.server_id.value: config.THIS_SERVER_ID,
            JSONKeys.auth_key.value: config.THIS_SERVER_AUTH_KEY,
            JSONKeys.server_url.value: f"http://3.126.63.200:{config.SERVER_PORT}/"}
    headers = {JSONKeys.client_data.value: "false", JSONKeys.shutdown.value: "false"}
    requests.post(config.WEB_INTERFACE, data=json.dumps(data), headers=headers)
    for mapping in BotQuizMapping.get_all_mappings(db.session):
        quiz_bot = QuizTelegramBot(manager, json.loads(mapping.quiz),
                                   mapping.table_name, mapping.user_id,
                                   bot_id=mapping.bot_id)
        quiz_bot.start_webhook(telegram_webhook_base)
        active_quiz_bots[mapping.bot_id] = quiz_bot


def start_server():
    app.run(host='0.0.0.0', port=config.SERVER_PORT, threaded=True)


def stop_server():
    data = {JSONKeys.server_id.value: config.THIS_SERVER_ID,
            JSONKeys.auth_key.value: config.THIS_SERVER_AUTH_KEY}
    headers = {JSONKeys.client_data.value: "false", JSONKeys.shutdown.value: "true"}
    requests.post(config.WEB_INTERFACE, data=json.dumps(data), headers=headers)
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running werkzeug')
    func()


def save_quiz(user_id, table_name, table_json, quiz_json):
    record = {QuizColumns.user_id.value: user_id,
              QuizColumns.table_name.value: table_name,
              QuizColumns.table.value: table_json,
              QuizColumns.quiz.value: quiz_json}
    Quiz.add_quiz(db.session, record)


def save_quiz_bot_mapping(bot_id, bot_username, user_id, table_name, quiz_json):
    record = {BotQuizColumns.bot_id.value: bot_id,
              BotQuizColumns.bot_username.value: bot_username,
              BotQuizColumns.user_id.value: user_id,
              BotQuizColumns.table_name.value: table_name,
              BotQuizColumns.quiz.value: quiz_json}
    BotQuizMapping.add_mapping(db.session, record)


def fetch_info(user_id):
    with db.get_engine().connect() as con:
        tables = []
        for table in get_all_tables(con, user_id).mappings().all():
            table = dict(table)
            table[JSONKeys.bots.value] = []
            table[JSONKeys.all_entries.value] = get_num_objects(
                con, table[JSONKeys.table_name.value], user_id)
            quiz = Quiz.get_quiz_with_user_id_and_table_name(
                db.session, user_id, table[JSONKeys.table_name.value])
            table[JSONKeys.new_entries.value] = get_num_objects_from_creation_date(
                con, table[JSONKeys.table_name.value], user_id, quiz.last_download)
            for mapping in BotQuizMapping.get_mappings_by_user_id(db.session, user_id):
                if table[JSONKeys.table_name.value] == mapping.table_name:
                    table[JSONKeys.bots.value].append(mapping.bot_username)
            tables.append(table)
        data = {JSONKeys.tables.value: tables}
        return Response(data.__str__(), status=200)


def fetch_quiz(table_name, user_id):
    if table_name is None:
        return Response("Table name parameter not found", status=400)
    quiz = Quiz.get_quiz_with_user_id_and_table_name(db.session, user_id, table_name)
    return Response(quiz.quiz.__str__(), status=200)


def fetch_excel(table_name, user_id):
    if table_name is None:
        return Response("Table name parameter not found", status=400)
    with db.get_engine().connect() as con:
        output = convert_list_of_dict_to_excel_table(get_all_objects(con, table_name, user_id))
    Quiz.set_last_download(db.session,
                           Quiz.get_quiz_with_user_id_and_table_name(db.session, user_id, table_name).id,
                           datetime.datetime.utcnow())
    return send_file(output, download_name=f'{table_name}.xlsx', as_attachment=True)


def fetch_csv(table_name, user_id):
    if table_name is None:
        return Response("Table name parameter not found", status=400)
    with db.get_engine().connect() as con:
        output = convert_list_of_dict_to_csv(get_all_objects(con, table_name, user_id))
    Quiz.set_last_download(db.session,
                           Quiz.get_quiz_with_user_id_and_table_name(db.session, user_id, table_name).id,
                           datetime.datetime.utcnow())
    return send_file(output, download_name=f'{table_name}.csv', as_attachment=True)


def create(request_body, user_id):
    table_dict = request_body.get(JSONKeys.table_json.value)
    table_name = None
    try:
        if table_dict:
            quiz_dict = request_body[JSONKeys.quiz_json.value]

            table_json = json.dumps(table_dict)
            quiz_json = json.dumps(quiz_dict)
            schema_name = create_schema(user_id)
            table_name = create_table(table_dict, schema_name)

            quiz_bot = QuizTelegramBot(manager, quiz_dict, table_name, schema_name)
            quiz_bot.start_webhook(telegram_webhook_base)
            active_quiz_bots[quiz_bot.bot.id] = quiz_bot

            save_quiz(user_id, table_name, table_json, quiz_json)
            save_quiz_bot_mapping(quiz_bot.bot.id, quiz_bot.get_telegram_username(),
                                  user_id, table_name, quiz_json)

            return Response(quiz_bot.get_telegram_username(), status=200)
        else:
            return Response("No table json found", status=400)
    except RuntimeError:
        if table_name is not None:
            with db.get_engine().connect() as con:
                drop_table(con, table_name, schema_name)
        return Response("Not enough bots", status=412)
    except KeyError:
        if table_name is not None:
            with db.get_engine().connect() as con:
                drop_table(con, table_name, schema_name)
        return Response("No quiz json found", status=400)


def update(request_body, user_id):
    table_name = request_body.get(JSONKeys.table_name.value)
    try:
        quiz_dict = request_body[JSONKeys.quiz_json.value]
        quiz_json = json.dumps(quiz_dict)
        if table_name:
            old_quiz = Quiz.get_quiz_with_user_id_and_table_name(db.session, user_id, table_name)
            Quiz.set_quiz(db.session, old_quiz.id, quiz_json)

            for mapping in BotQuizMapping.get_mappings_with_user_id_and_table_name(db.session, user_id, table_name):
                if mapping.bot_id in active_quiz_bots:
                    active_quiz_bots[mapping.bot_id].discharge_bot()
                    del active_quiz_bots[mapping.bot_id]

                    quiz_bot = QuizTelegramBot(manager, quiz_dict, mapping.table_name,
                                               mapping.user_id, bot_id=mapping.bot_id)
                    quiz_bot.start_webhook(telegram_webhook_base)
                    active_quiz_bots[mapping.bot_id] = quiz_bot

                BotQuizMapping.set_quiz(db.session, mapping.bot_id, quiz_json)
            return Response(status=200)
        else:
            return Response("Table name parameter not found", status=400)
    except KeyError:
        return Response("No quiz json found", status=400)


def delete(request_body, user_id):
    table_name = request_body.get(JSONKeys.table_name.value)
    if table_name:
        for mapping in BotQuizMapping.get_mappings_with_user_id_and_table_name(db.session, user_id, table_name):
            if mapping.bot_id in active_quiz_bots:
                active_quiz_bots[mapping.bot_id].discharge_bot()
                del active_quiz_bots[mapping.bot_id]
        Quiz.delete_quiz_with_user_id_and_table_name(db.session, user_id, table_name)
        BotQuizMapping.delete_mappings_with_user_id_and_table_name(db.session, user_id, table_name)
        with db.get_engine().connect() as con:
            drop_table(con, table_name, user_id)
        return Response("Success", status=200)
    else:
        return Response("Table name parameter not found", status=400)


def stop(request_body, user_id):
    pass


def fetch(request_body, user_id):
    fetch_what = request_body.get(JSONKeys.fetch_what.value)
    table_name = request_body.get(JSONKeys.table_name.value)
    if fetch_what == FetchKeywords.info.value:
        return fetch_info(user_id)
    elif fetch_what == FetchKeywords.quiz.value:
        return fetch_quiz(table_name, user_id)
    elif fetch_what == FetchKeywords.excel.value:
        return fetch_excel(table_name, user_id)
    elif fetch_what == FetchKeywords.csv.value:
        return fetch_csv(table_name, user_id)
    else:
        return Response("Unknown or absent fetch_what parameter", status=400)


def check(request_body, user_id):
    table_name = request_body.get(JSONKeys.table_name.value)
    if table_name:
        if Quiz.get_quiz_with_user_id_and_table_name(db.session, user_id, table_name):
            return Response("true", status=200)
        else:
            return Response("false", status=200)
    else:
        return Response("Table name parameter not found", status=400)


@app.route('/', methods=['POST'])
def web_interface_receive():
    request_body = json.loads(request.get_data().decode('utf-8'))
    user_id = request_body.get(JSONKeys.user_identifier.value)
    keyword = request_body.get(JSONKeys.request_keyword.value)
    if keyword == RequestKeywords.create.value and user_id:
        return create(request_body, user_id)
    elif keyword == RequestKeywords.update.value and user_id:
        return update(request_body, user_id)
    elif keyword == RequestKeywords.fetch.value and user_id:
        return fetch(request_body, user_id)
    elif keyword == RequestKeywords.check.value:
        return check(request_body, user_id)
    elif keyword == RequestKeywords.stop.value:
        return stop(request_body, user_id)
    elif keyword == RequestKeywords.delete.value and user_id:
        return delete(request_body, user_id)
    else:
        return Response("Incorrect JSON format", status=400)


@app.route('/telegram/<bot_id>', methods=['POST'])
def process_telegram(bot_id):
    try:
        active_quiz_bots[uuid.UUID(bot_id)].process_request(request.get_data().decode('utf-8'))
    except KeyError:
        print("Bot is already stopped or removed")
    return Response(status=200)


@app.route('/add-bot', methods=['POST'])
def add_bot():
    add_request = json.loads(request.get_data().decode('utf-8'))
    manager.add_new_bot(add_request[JSONKeys.api_token.value])
    return Response(status=200)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutting down server!")
    for quiz_bot_id in active_quiz_bots:
        active_quiz_bots[quiz_bot_id].discharge_bot()
    active_quiz_bots.clear()
    stop_server()
    return Response(status=200)


if __name__ == '__main__':
    connect = False
    db.create_all()
    db.session.commit()
    while not connect:
        try:
            init()
            connect = True
        except ConnectionError:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except NewConnectionError:
            pass
        except MaxRetryError:
            pass
    start_server()
