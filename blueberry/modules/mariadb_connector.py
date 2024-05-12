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
            create_users_query = """
                create table if not exists users (
                id int auto_increment primary key,
                login varchar(255) not null,
                password_sha256 varchar(255) not null,
                unique (login)
                );
                """
            cursor.execute(create_users_query)

            create_tokens_query = """
                create table if not exists tokens (
                id int auto_increment primary key,
                user_id int not null,
                token varchar(255) not null,
                expires int not null
                );
                """
            cursor.execute(create_tokens_query)

        self.connection.commit()

    def register(self, login: str, password: str) -> str:
        """
        Registers user and gives initial token
        """
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()

        # Check if user exists
        select_query = f"select login from users where login='{login}'"
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount != 0:
                raise LoginTakenError("Login is taken")

        # Register user
        insert_query = f"insert into users (login, password_sha256) values ('{login}', '{password_sha256}');"
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(insert_query)
                inserted_id = cursor.lastrowid
                self.connection.commit()
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

        # Give user a token
        initial_token = create_token(login)
        expiery_time = int(time.time() + datetime.timedelta(days=1).total_seconds())
        insert_query = f"insert into tokens (user_id, token, expires) values ('{inserted_id}', '{initial_token}', '{expiery_time}');"
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(insert_query)
                self.connection.commit()
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

    def authentificate_user(self, login: str, password: str) -> str:
        """
        Authentificates user and generates token
        """
        password_sha256 = hashlib.sha256(password.encode()).hexdigest()
        select_query = f"select id, password_sha256 from users where login='{login}';"

        # Check password
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount == 0:
                return False

            fetched = cursor.fetchone()
            user_id = fetched[0]
            saved_password = fetched[1]

            if saved_password != password_sha256:
                return False

        # Create token
        token = create_token(login)
        expiery_time = int(time.time() + datetime.timedelta(days=1).total_seconds())
        update_query = f"insert into tokens (user_id, token, expires) values ('{user_id}', '{token}', '{expiery_time}');"
        self.connection.ping(reconnect=True)
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
        # Get user id
        select_query = f"select id from users where login='{login}';"
        self.connection.ping(reconnect=True)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount == 0:
                return False

            user_id = cursor.fetchone()[0]

        # Check token (Select with user id too for additional security)
        select_query = (
            f"select expires from tokens where user_id='{user_id}' and token='{token}';"
        )
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(select_query)
            except Exception as exc:
                raise MariaDBError(exc.args) from exc

            if cursor.rowcount == 0:
                return False

            expiery_time = cursor.fetchone()[0]

        # Delete token if it is too old
        if expiery_time < (
            int(time.time() + datetime.timedelta(days=1).total_seconds())
        ):
            delete_query = (
                f"delete from tokens where user_id='{user_id}' and token='{token}'"
            )
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(delete_query)
                    self.connection.commit()
                except Exception as exc:
                    raise MariaDBError(exc.args) from exc

            return False

        return True
