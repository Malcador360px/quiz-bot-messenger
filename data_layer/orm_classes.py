import datetime
import dateutil.parser
import pytz
import uuid
from enums.columns import BotColumns, BotQuizColumns, QuizColumns
from sqlalchemy.dialects.postgresql import UUID, JSONB
from data_layer.db_app import db


class Bot(db.Model):
    __tablename__ = 'bots'
    id = db.Column(BotColumns.id.value, UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_token = db.Column(BotColumns.api_token.value, db.Text, unique=True, nullable=False)
    active = db.Column(BotColumns.active.value, db.Boolean, default=False, nullable=False)
    created = db.Column(BotColumns.created.value, db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(BotColumns.updated.value, db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def add_bot(cls, session, record: dict):
        bot = cls.create_bot(record)
        session.add(bot)
        session.commit()

    @classmethod
    def create_bot(cls, record: dict):
        data_dict = {
            "api_token": record[BotColumns.api_token.value]
        }
        bot_id = record.get(BotColumns.id.value)
        if bot_id:
            data_dict["id"] = bot_id
        active = record.get(BotColumns.active.value)
        if active:
            data_dict["active"] = active
        updated = record.get(BotColumns.updated.value)
        if updated:
            data_dict[updated] = dateutil.parser.parse(
                updated
            ).replace(tzinfo=pytz.utc)

        return cls(**data_dict)

    @classmethod
    def get_bot_by_id(cls, session, bot_id):
        return session.query(cls).filter(cls.id == bot_id).first()

    @classmethod
    def get_bot_by_token(cls, session, token):
        return session.query(cls).filter(cls.api_token == token).first()

    @classmethod
    def get_idle_bot(cls, session):
        return session.query(cls).filter(cls.active == False).first()

    @classmethod
    def get_all_bots_from_date(cls, session, date):
        return session.query(cls).filter(cls.updated >= date).all()

    @classmethod
    def set_active(cls, session, bot_id, active):
        session.query(cls).filter(cls.id == bot_id).update({BotColumns.active.value: active})
        session.commit()

    @classmethod
    def delete_bot_by_id(cls, session, bot_id):
        session.query(cls).filter(cls.id == bot_id).delete()
        session.commit()


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    __table_args__ = (db.UniqueConstraint('user_id', 'table_name', name='_user_id_table_name_uc'), )
    id = db.Column(QuizColumns.id.value, UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(QuizColumns.user_id.value, db.Text, nullable=False)
    table_name = db.Column(QuizColumns.table_name.value, db.Text, nullable=False)
    table = db.Column(QuizColumns.table.value, JSONB, nullable=False)
    quiz = db.Column(QuizColumns.quiz.value, JSONB, nullable=False)
    last_download = db.Column(QuizColumns.last_download.value, db.DateTime, default=datetime.datetime.utcnow)
    created = db.Column(QuizColumns.created.value, db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(QuizColumns.updated.value, db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def add_quiz(cls, session, record: dict):
        quiz = cls.create_quiz(record)
        session.add(quiz)
        session.commit()

    @classmethod
    def create_quiz(cls, record: dict):
        data_dict = {
            "user_id": record[QuizColumns.user_id.value],
            "table_name": record[QuizColumns.table_name.value],
            "table": record[QuizColumns.table.value],
            "quiz": record[QuizColumns.quiz.value]
        }
        quiz_id = record.get(QuizColumns.id.value)
        if quiz_id:
            data_dict["id"] = quiz_id
        updated = record.get(QuizColumns.updated.value)
        if updated:
            data_dict[updated] = dateutil.parser.parse(
                updated
            ).replace(tzinfo=pytz.utc)

        return cls(**data_dict)

    @classmethod
    def get_all_quizzes(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_quiz_by_id(cls, session, quiz_id):
        return session.query(cls).filter(cls.id == quiz_id).first()

    @classmethod
    def get_quizzes_by_user_id(cls, session, user_id):
        return session.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_quiz_with_user_id_and_table_name(cls, session, user_id, table_name):
        return session.query(cls).filter(cls.user_id == user_id).filter(cls.table_name == table_name).first()

    @classmethod
    def get_all_quizzes_from_date(cls, session, date):
        return session.query(cls).filter(cls.updated >= date).all()

    @classmethod
    def set_quiz(cls, session, quiz_id, quiz):
        session.query(cls).filter(cls.id == quiz_id).update({QuizColumns.quiz.value: quiz})
        session.commit()

    @classmethod
    def set_last_download(cls, session, quiz_id, last_download):
        session.query(cls).filter(cls.id == quiz_id).update({QuizColumns.last_download.value: last_download})
        session.commit()

    @classmethod
    def delete_bot_by_id(cls, session, quiz_id):
        session.query(cls).filter(cls.id == quiz_id).delete()
        session.commit()

    @classmethod
    def delete_quiz_with_user_id_and_table_name(cls, session, user_id, table_name):
        session.query(cls).filter(cls.user_id == user_id).filter(cls.table_name == table_name).delete()
        session.commit()


class BotQuizMapping(db.Model):
    __tablename__ = 'bots_quizzes'
    bot_id = db.Column(BotQuizColumns.bot_id.value, UUID(as_uuid=True), primary_key=True)
    bot_username = db.Column(BotQuizColumns.bot_username.value, db.Text, nullable=False)
    user_id = db.Column(BotQuizColumns.user_id.value, db.Text, nullable=False)
    table_name = db.Column(BotQuizColumns.table_name.value, db.Text, nullable=False)
    quiz = db.Column(BotQuizColumns.quiz.value, JSONB, nullable=False)
    created = db.Column(BotQuizColumns.created.value, db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(BotQuizColumns.updated.value, db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def add_mapping(cls, session, record: dict):
        mapping = cls.create_mapping(record)
        session.add(mapping)
        session.commit()

    @classmethod
    def create_mapping(cls, record: dict):
        data_dict = {
            "bot_id": record[BotQuizColumns.bot_id.value],
            "bot_username": record[BotQuizColumns.bot_username.value],
            "user_id": record[BotQuizColumns.user_id.value],
            "table_name": record[BotQuizColumns.table_name.value],
            "quiz": record[BotQuizColumns.quiz.value]
        }
        updated = record.get(BotQuizColumns.updated.value)
        if updated:
            data_dict[updated] = dateutil.parser.parse(
                updated
            ).replace(tzinfo=pytz.utc)

        return cls(**data_dict)

    @classmethod
    def get_all_mappings(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_mapping_by_bot_id(cls, session, bot_id):
        return session.query(cls).filter(cls.bot_id == bot_id).first()

    @classmethod
    def get_mappings_by_user_id(cls, session, user_id):
        return session.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_mappings_with_user_id_and_table_name(cls, session, user_id, table_name):
        return session.query(cls).filter(cls.user_id == user_id).filter(cls.table_name == table_name).all()

    @classmethod
    def get_all_mappings_from_date(cls, session, date):
        return session.query(cls).filter(cls.updated >= date).all()

    @classmethod
    def set_quiz(cls, session, bot_id, quiz):
        session.query(cls).filter(cls.bot_id == bot_id).update({BotQuizColumns.quiz.value: quiz})
        session.commit()

    @classmethod
    def delete_mapping_by_bot_id(cls, session, bot_id):
        session.query(cls).filter(cls.bot_id == bot_id).delete()
        session.commit()

    @classmethod
    def delete_mappings_with_user_id_and_table_name(cls, session, user_id, table_name):
        session.query(cls).filter(cls.user_id == user_id).filter(cls.table_name == table_name).delete()
        session.commit()
