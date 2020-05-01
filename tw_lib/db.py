import sqlite3
from .schema import SCHEMA


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Should rather use not nulls
def create_table_query(table_name, table_cols):
    create_table = f"CREATE TABLE {table_name} ({','.join(table_cols)})"
    return create_table


# Should rather use values and specify the rows
def insert_query(table_name, row):
    keys = ",".join(row.keys())
    values = ",".join(["?" for i in range(len(row))])
    return f"""insert into {table_name} ({keys}) VALUES ({values})"""


def insert_table(conn, table_name, rows):
    for row in rows:
        query = insert_query(table_name, row), list(row.values())
        conn.execute(*query)


def truncate_table(conn, table_name):
    conn.execute(f"DROP TABLE {table_name}")
    conn.execute(create_table_query(table_name, SCHEMA[table_name]))


class Database:
    def __init__(self, db_name):
        self._db_name = db_name

    def bootstrap(self):
        with sqlite3.connect(self._db_name) as conn:
            for table, schema in SCHEMA.items():
                conn.execute(create_table_query(table, schema))

    def get_latest_time_entries(self, start_time, row_factory=dict_factory):
        with sqlite3.connect(self._db_name) as conn:
            conn.row_factory = dict_factory
            data = conn.execute(
                f"""
                SELECT start, duration, name
                FROM time_entries LEFT JOIN project ON pid=project.id
                WHERE DATE(start) > ? AND name IN (SELECT name FROM project_name);
                """,
                (start_time,),
            ).fetchall()
        return data

    def update_table(self, table, values):
        with sqlite3.connect(self._db_name) as conn:
            truncate_table(conn, table)
            insert_table(conn, table, values)