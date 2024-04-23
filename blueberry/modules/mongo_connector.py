from pymongo import MongoClient

from models.recipe_models import (
    RecipeForList,
    RecipeForUI,
    StepForUI,
)

from modules.config import (
    MONGO_PORT,
    MONGO_USER,
    MONGO_PASSWORD,
    MONGO_DB,
)


class MongoError(RuntimeError):
    pass


class MongoConnector:

    def __init__(self):
        CONNECTION_STRING = (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@mongo:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
        )
        client = MongoClient(CONNECTION_STRING)
        self.client_db = client["blueberry"]
        self.collection = self.client_db["recipes"]

    def get(self, id: str) -> RecipeForUI:
        try:
            value = self.collection.find_one({"id": id})
        except Exception as exc:
            raise MongoError(exc.args) from exc
        return RecipeForUI.model_validate(value)

    def get_all(self) -> list[RecipeForList]:
        try:
            values = [
                RecipeForUI.model_validate(value) for value in self.collection.find()
            ]
        except Exception as exc:
            raise MongoError(exc.args) from exc
        return values

    def set(self, value: RecipeForUI) -> int:
        next_id = self.count()
        value.id = next_id
        try:
            dumped_dict = value.model_dump()
            print(dumped_dict)
            self.collection.insert_one(dumped_dict)
        except Exception as exc:
            raise MongoError(exc.args) from exc
        return next_id

    def count(self) -> int:
        try:
            count =  self.collection.count_documents({})
        except Exception as exc:
            raise MongoError(exc.args) from exc
        return count