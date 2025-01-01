import datetime
import uuid
from enums.input_structure import JSONKeys
from enums.columns import ColumnTypes, StandardColumns
from sqlalchemy import MetaData, inspect, schema, Table, Column, DateTime, Text, Integer
from data_layer.db_app import db


def create_schema(schema_name):
    engine = db.get_engine()
    if not engine.dialect.has_schema(engine, schema_name):
        engine.execute(schema.CreateSchema(schema_name))
    return schema_name


def create_table(table_structure, schema_name):
    meta = MetaData()
    engine = db.get_engine()
    table_name = table_structure.pop(JSONKeys.table_name.value)
    columns = table_structure
    if not inspect(engine).has_table(table_name):
        table = Table(table_name, meta, Column(StandardColumns.id.value, Text, primary_key=True, default=uuid.uuid4),
                      Column(StandardColumns.messenger_id.value, Text),
                      Column(StandardColumns.created.value, DateTime, default=datetime.datetime.utcnow),
                      Column(StandardColumns.updated.value, DateTime, default=datetime.datetime.utcnow))
        table.schema = schema_name
        for column_name in columns.keys():
            table.append_column(Column(column_name, __assign_type(columns[column_name])))
        meta.create_all(engine)
        db.session.commit()
    else:
        print("Table with this name already exists.")
    return table_name


def __assign_type(type_str, default=Text):
    if type_str == ColumnTypes.integer.value:
        return Integer
    if type_str == ColumnTypes.text.value:
        return Text
    if type_str == ColumnTypes.datetime.value:
        return DateTime
    return default


def get_all_tables(connection, schema_name):
    return connection.execute(f'SELECT table_name FROM information_schema.tables'
                              f' WHERE table_schema=\'{schema_name}\' AND table_type=\'BASE TABLE\'')


def get_all_objects(connection, table_name, schema_name):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"').mappings().all()


def get_num_objects(connection, table_name, schema_name):
    return connection.execute(f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"').scalar()


def get_object_by_id(connection, table_name, schema_name, record_id):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.id.value}" = \'{record_id}\'').mappings().all()


def get_objects_by_messenger_id(connection, table_name, schema_name, messenger_id):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.messenger_id.value}" = \'{messenger_id}\'').mappings().all()


def get_objects_from_creation_date(connection, table_name, schema_name, date):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.created.value}"'
                              f' > CAST(\'{date}\' AS TIMESTAMP)').mappings().all()


def get_num_objects_from_creation_date(connection, table_name, schema_name, date):
    return connection.execute(f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.created.value}"'
                              f' > CAST(\'{date}\' AS TIMESTAMP)').scalar()


def get_objects_from_update_date(connection, table_name, schema_name, date):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.updated.value}"'
                              f' > CAST(\'{date}\' AS TIMESTAMP)').mappings().all()


def get_objects_til_creation_date(connection, table_name, schema_name, date):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.created.value}"'
                              f' < CAST(\'{date}\' AS TIMESTAMP)').mappings().all()


def get_objects_til_update_date(connection, table_name, schema_name, date):
    return connection.execute(f'SELECT * FROM "{schema_name}"."{table_name}"'
                              f' WHERE "{StandardColumns.updated.value}"'
                              f' < CAST(\'{date}\' AS TIMESTAMP)').mappings().all()


def drop_table(connection, table_name, schema_name):
    return connection.execute(f'DROP TABLE "{schema_name}"."{table_name}"')


def drop_schema(connection, schema_name):
    return connection.execute(f'DROP SCHEMA "{schema_name}" CASCADE')
