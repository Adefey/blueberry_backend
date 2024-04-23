import os

MONGO_PORT = os.environ.get("DB_PORT")
MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DB = os.environ.get("MONGO_INITDB_DATABASE")
