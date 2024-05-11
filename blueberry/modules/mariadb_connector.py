import pymysql
import hashlib
import datetime
import time
from modules.utils import create_token

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
                token varchar(255),
                expires int,
                unique (login)
                );
                """
            cursor.execute(create_table_query)
        self.connection.commit()

    def register(self, login: str, password: str) -> str:
        """
        Registers user and gives initial token
        """
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()

        select_query = f"select login from users where login='{login}'"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount != 0:
                raise LoginTakenError("Login is taken")
        initial_token = create_token(login)
        expiery_time = int(time.time()) + datetime.timedelta(days=1).total_seconds()
        insert_query = f"insert into users (login, password_sha256, expires) values ('{login}', '{password_sha256}', '{initial_token}', '{expiery_time}');"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(insert_query)
                self.connection.commit()
                return initial_token
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

    def authentificate_user(self, login: str, password: str) -> str:
        """
        Authentificates user and generates token
        """
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()
        select_query = f"select password_sha256 from users where login='{login}';"

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount == 0:
                return False

            saved_password = cursor.fetchone()[0]

            if saved_password != password_sha256:
                return False

        token = create_token(login)
        expiery_time = int(time.time()) + datetime.timedelta(days=1).total_seconds()
        update_query = f"update users set token = '{token}' expires = '{expiery_time}' where login = '{login}'"

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(update_query)
                self.connection.commit()
                return token
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

    def check_token(self, login: str, token: str) -> bool:
        """
        Check user token
        """
        select_query = f"select token, expires from users where login='{login}';"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount == 0:
                return False

            result = cursor.fetchone()
            saved_token = result[0]
            expiery_time = result[1]

            if expiery_time > (
                int(time.time()) + datetime.timedelta(days=1).total_seconds()
            ):
                update_query = f"update users set token = NULL expires = NULL where login = '{login}'"
                with self.connection.cursor() as cursor:
                    try:
                        cursor.execute(update_query)
                        self.connection.commit()
                    except Exception as exc:
                        raise MariaDBError(exc.args) from exc

                return False

            return saved_token == token
