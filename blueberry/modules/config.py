import os

AUTH_SECRET = os.environ.get("AUTH_SECRET")

MONGO_PORT = int(os.environ.get("DB_PORT"))
MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DB = os.environ.get("MONGO_INITDB_DATABASE")

MYSQL_TCP_PORT = int(os.environ.get("MYSQL_TCP_PORT"))
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_ROOT_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
