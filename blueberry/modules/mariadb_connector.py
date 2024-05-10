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


class LoginTakenError(MariaDBError):
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
                password_sha256 varchar(255) not null,
                unique (login)
                );
                """
            cursor.execute(create_table_query)
        self.connection.commit()

    def register(self, login: str, password: str):
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()

        select_query = f"select login from users where login='{login}'"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount != 0:
                raise LoginTakenError("Login is taken")

        insert_query = f"insert into users (login, password_sha256) values ('{login}', '{password_sha256}');"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(insert_query)
                self.connection.commit()
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

    def check_user(self, login: str, password: str):
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()
        select_query = f"select password_sha256 from users where login='{login}';"

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc
            saved_password = cursor.fetchone()[0]

        return saved_password == password_sha256
