import pymysql
import hashlib

from modules.config import (
    MYSQL_TCP_PORT,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_USER,
)


class MariaDBError(Exception):
    pass


class MariaDB:
    def __init__(self):
        self.params = {
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "host": "mariadb",
            "database": MYSQL_DATABASE,
            "port": MYSQL_TCP_PORT,
        }
        self.connection = pymysql.connect(**self.params)
        with self.connection.cursor() as cursor:
            create_table_query = """
                create table if not exists users (
                id int auto_increment primary key,
                login varchar(255) not null,
                password_sha256 varchar(255) not null
                );
                """
            cursor.execute(create_table_query)
        self.connection.commit()

    def register(self, login: str, password: str):
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()
        insert_query = f"insert into users (login, password_sha256) values ('{login}', '{password_sha256}');"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query)
            self.connection.commit()
        except Exception as exc:
            raise MariaDBError(exc.args) from exc

    def check_user(self, login: str, password: str):
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()
        select_query = f"select password_sha256 from users where login='{login}';"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_query)
                saved_password = cursor.fetchone()[0]
        except Exception as exc:
            raise MariaDBError(exc.args) from exc

        return saved_password == password_sha256
